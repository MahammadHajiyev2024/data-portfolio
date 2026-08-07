# main.py
from src.database import init_db
from src.ingestion import extract_fred_data, transform_and_load

def main():
    print("🚀 Step 1: Initializing DuckDB database and schemas...")
    init_db()
    
    print("📥 Step 2: Extracting fresh indicators from FRED...")
    symbols = ["DGS10", "DCOILWTICO"]
    raw_data = extract_fred_data(symbols)
    
    print("⚙️ Step 3: Transforming and executing Upsert into Production tables...")
    transform_and_load(raw_data)
    
    print("✅ Pipeline executed successfully!")

if __name__ == "__main__":
    main()