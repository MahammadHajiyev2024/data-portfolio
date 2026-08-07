# src/ingestion.py
import pandas as pd
import requests
import io
from src.database import get_connection

def extract_fred_data(symbols: list) -> pd.DataFrame:
    """Fetches raw time-series data directly from FRED CSV endpoints."""
    df_list = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for symbol in symbols:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={symbol}"
        
        # Download raw content with browser headers to avoid request block
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Load CSV from bytes
        data = pd.read_csv(io.StringIO(response.text))
        
        # Standardize column headers to lowercase
        data.columns = [col.strip().lower() for col in data.columns]
        
        # Identify date column (matches 'date' or 'observation_date')
        date_col = next((c for c in data.columns if 'date' in c), None)
        if not date_col:
            raise KeyError(f"Could not find date column in FRED response. Found columns: {list(data.columns)}")
            
        data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
        data = data.rename(columns={date_col: "metric_date", symbol.lower(): symbol})
        
        df_list.append(data[["metric_date", symbol]])

    # Merge datasets cleanly on metric_date
    combined_df = df_list[0]
    for next_df in df_list[1:]:
        combined_df = pd.merge(combined_df, next_df, on="metric_date", how="outer")

    return combined_df

def transform_and_load(raw_df: pd.DataFrame):
    """Cleans data and merges it into production analytical layers using DuckDB."""
    # 1. Clean data in Pandas (Type safety & Interpolation)
    raw_df["DGS10"] = pd.to_numeric(raw_df["DGS10"], errors="coerce")
    raw_df["DCOILWTICO"] = pd.to_numeric(raw_df["DCOILWTICO"], errors="coerce")
    
    # Sort and fill holiday/weekend gaps safely
    cleaned_df = raw_df.sort_values("metric_date").ffill()
    
    # Filter down to the active project window (e.g., 2023 onward)
    cleaned_df = cleaned_df[cleaned_df["metric_date"] >= "2023-01-01"]

    # 2. Leverage DuckDB for an Upsert operation (Idempotency)
    # Using 'cleaned_df' directly in the query strings works seamlessly with DuckDB
    with get_connection() as con:
        con.execute("""
            INSERT OR REPLACE INTO fact_macro_metrics (metric_date, yield_10y, oil_wti)
            SELECT 
                metric_date, 
                DGS10 as yield_10y, 
                DCOILWTICO as oil_wti 
            FROM cleaned_df;
        """)