# src/database.py
import duckdb
from pathlib import Path

# Anchor path relative to this file's location:
# __file__ -> src/database.py
# .parent  -> src/
# .parent  -> 01-analytics-pipeline-duckdb/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "macro_analytics.duckdb"

def get_connection() -> duckdb.DuckDBPyConnection:
    """Establishes and returns a connection to the persistent DuckDB file."""
    # Ensure the data directory exists inside project root
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))

def init_db() -> None:
    """Initializes the database schema using explicit DDL statements."""
    with get_connection() as con:
        # Using explicit DDL is more professional than letting Pandas infer types
        con.execute("""
            CREATE TABLE IF NOT EXISTS staging_macro_indicators (
                file_date DATE,
                symbol VARCHAR,
                value DOUBLE
            );
        """)
        
        con.execute("""
            CREATE TABLE IF NOT EXISTS fact_macro_metrics (
                metric_date DATE PRIMARY KEY,
                yield_10y DOUBLE,
                oil_wti DOUBLE,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)