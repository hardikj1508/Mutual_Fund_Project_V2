import json
from pathlib import Path

import pandas as pd

from getpass import getpass
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy import inspect

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
INVENTORY_PATH = PROJECT_ROOT / "data" / "processed" / "source_inventory.json"

DATABASE_NAME = "bluestock_mf_v2"
DATABASE_USER = "postgres"
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
DATABASE_SCHEMA = "staging"

TABLE_MAPPING = {
    "01_fund_master.csv": "fund_master",
    "02_nav_history.csv": "nav_history",
    "03_aum_by_fund_house.csv": "aum_by_fund_house",
    "04_monthly_sip_inflows.csv": "monthly_sip_inflows",
    "05_category_inflows.csv": "category_inflows",
    "06_industry_folio_count.csv": "industry_folio_count",
    "07_scheme_performance.csv": "scheme_performance",
    "08_investor_transactions.csv": "investor_transactions",
    "09_portfolio_holdings.csv": "portfolio_holdings",
    "10_benchmark_indices.csv": "benchmark_indices"
}

def create_database_engine():

    password = getpass("postgreSQL password: ")

    Connection_url = URL.create(
        drivername="postgresql+psycopg",
        username=DATABASE_USER,
        password=password,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME
    )

    return create_engine(Connection_url)

def load_source_inventory() -> list[dict]:

    with INVENTORY_PATH.open("r", encoding="utf-8") as file:
        inventory = json.load(file)

    if not isinstance(inventory, list):
        raise ValueError("Source inventory must contain a list.")

    return inventory

def validate_source_files(inventory: list[dict]) -> None:

    for source in inventory:
        file_name = source["file_name"]
        file_path = RAW_DATA_DIR / file_name

        if not file_path.is_file():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        df = pd.read_csv(file_path)

        expected_columns = source["columns"]
        expected_rows = source["row_count"]

        if list(df.columns) != expected_columns:
            raise ValueError(
                f"Column mismatch in {file_name}.\n"
                f"Expected: {expected_columns}\n"
                f"Found: {list(df.columns)}"
            )

        if len(df) != expected_rows:
            raise ValueError(
                f"Row-count mismatch in {file_name}: "
                f"expected {expected_rows}, found {len(df)}"
            )

        print(
            f"PASS | {file_name} | "
            f"{len(df):,} rows | {len(df.columns)} columns"
        )

def load_csv_to_staging(engine, inventory:list[dict]) -> None:

    for source in inventory:
        file_name = source["file_name"]
        table_name = TABLE_MAPPING[file_name]
        file_path = RAW_DATA_DIR / file_name

        df = pd.read_csv(file_path, dtype=str, keep_default_na=False)

        print(f"\nLoading {file_name} -> staging.{file_name}")

        df.to_sql(
            name=table_name,
            con=engine,
            schema=DATABASE_SCHEMA,
            if_exists="replace",
            index=False,
            chunksize=1000,
            method="multi"
        )

        with engine.connect() as connection:
            loaded_count = connection.execute(
                text(f'SELECT COUNT(*) FROM "{DATABASE_SCHEMA}"."{table_name}"')
            ).scalar_one()

        expected_count = source["row_count"]

        if loaded_count != expected_count:
            raise RuntimeError(
                f"Row-count mismatch for {table_name}: "
                f"expected {expected_count}, loaded {loaded_count}"
            )

        print(
            f"PASS | staging.{table_name} | "
            f"{loaded_count:,} rows loaded"
        )

if __name__ == "__main__":
    source_inventory = load_source_inventory()
    validate_source_files(source_inventory)

    print("\nAll source files passed structural validation.")

    engine = create_database_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database(), current_user"))
            print("DATABASE connection successful:", result.one())

        load_csv_to_staging(engine, source_inventory)

        print("\nAll staging tables loaded successfully.")

    finally:
        engine.dispose()
    