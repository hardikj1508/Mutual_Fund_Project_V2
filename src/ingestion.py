from pathlib import Path
import pandas as pd
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

INVENTORY_PATH = PROCESSED_DATA_DIR / "source_inventory.json"

def inspect_source_files():
    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DATA_DIR}"
        )
    
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in: {RAW_DATA_DIR}"
        )
    
    inventory = []
    
    print(f"Raw data directory: {RAW_DATA_DIR}")
    print(f"CSV files found: {len(csv_files)}")
    print("-" * 55)
    
    for file_path in csv_files:
        
        df = pd.read_csv(file_path)
        
        record = {
            "file_name": file_path.name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist()
        }
        
        inventory.append(record)
        
        print(
            f"{file_path.name:<35} "
            f"Rows: {len(df):>6,} | "
            f"Columns: {len(df.columns):>2}"
        )
    
    total_rows = sum(
        record["row_count"] for record in inventory
    )
    
    print("-" * 70)
    print(f"Total CSV files: {len (inventory)}")
    print(f"Total source rows: {total_rows:,}")
    
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    with INVENTORY_PATH.open("w", encoding="utf-8") as file:
        json.dump(inventory, file, indent=4)
    
    print("-" * 70)
    print(f"Inventory saved to: {INVENTORY_PATH}")

if __name__ == "__main__":
    inspect_source_files()
