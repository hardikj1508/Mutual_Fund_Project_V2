from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

def validate_fund_master():

    file_path = RAW_DATA_DIR / "01_fund_master.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Sorce file not found: {file_path}")

    df = pd.read_csv(file_path)

    print("DATA QUALITY REPORT: FUND MASTER")
    print("=" * 45)

    required_columns = [
        "amfi_code", "fund_house", "scheme_name", "category", "plan"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print(f"FAIL: Missing columns: {missing_columns}")
    else:
        print("PASS: All required columns are present")

    if not missing_columns:
        missing_values = df[required_columns].isna().sum()
        total_missing = int(missing_values.sum())

        if total_missing == 0:
            print("PASS: No missing values in required fields")

        else:
            print("FAIL: Missing values found:")
            print(missing_values[missing_values > 0])

    if "amfi_code" in df.columns:
        duplicate_count = int(df["amfi_code"].duplicated().sum())

        if duplicate_count == 0:
            print("PASS: AMFI codes are unique")

        null_codes = int(df["amfi_code"].isna().sum())

        if null_codes == 0:
            print("PASS: No missing AMFI codes")
        else:
            print(f"FAIL: Missinf AMFI codes: {null_codes}")

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

def validate_nav_history():

    file_path = RAW_DATA_DIR / "02_nav_history.csv"
    fund_master_path = RAW_DATA_DIR / "01_fund_master.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"NAV file not found: {file_path}")

    if not fund_master_path.exists():
        raise FileNotFoundError(
            f"Fund master not found: {fund_master_path}"
        )

    df = pd.read_csv(file_path)
    funds = pd.read_csv(fund_master_path)

    print("\nDATA QUALITY REPORT: NAV HISTORY")
    print("-" * 45)

    required_columns = ["amfi_code", "date", "nav"]
    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        print(f"FAIL: Missing columns: {missing_columns}")
        return

    print("PASS: All required columns are present")

    missing_values = df[required_columns].isna().sum()
    total_missing = int(missing_values.sum())

    if total_missing == 0:
        print("PASS: No missing values in required columns")
    else:
        print(f"FAIL: {total_missing} missing values found")
        print(missing_values[missing_values > 0])

    codes = pd.to_numeric(df["amfi_code"], errors="coerce")
    dates = pd.to_datetime(df["date"], errors="coerce")
    nav_values = pd.to_numeric(df["nav"], errors="coerce")

    invalid_codes = int(codes.isna().sum())
    invalid_dates = int(dates.isna().sum())
    invalid_nav = int(nav_values.isna().sum())

    print(
        f"{'PASS' if invalid_codes == 0 else 'FAIL'}: "
        f"AMFI code conversion; invalid rows: {invalid_codes}"
    )
    print(
        f"{'PASS' if invalid_dates == 0 else 'FAIL'}: "
        f"Date parsing; invalid rows: {invalid_dates}"
    )
    print(
        f"{'PASS' if invalid_nav == 0 else 'FAIL'}: "
        f"NAV numeric conversion; invalid rows: {invalid_nav}"
    )

    valid_key_rows = codes.notna() & dates.notna()
    duplicate_count = int(
        pd.DataFrame({
            "amfi_code": codes[valid_key_rows],
            "date": dates[valid_key_rows],        
        }).duplicated().sum()
    )
    print(
        f"{'PASS' if duplicate_count == 0 else 'FAIL'}: "
        f"Duplicate fund-date combinations: {duplicate_count}"
    )

    invalid_positive_count = int(
        (nav_values.notna() & (nav_values <= 0)).sum()
    )

    print(
        f"{'PASS'if invalid_positive_count == 0 else 'FAIL'}: "
        f"Non-positive NAV values: {invalid_positive_count}"
    )

    validate_fund_codes = set(
        pd.to_numeric(
            funds["amfi_code"], errors="coerce"
        ).dropna()
    )

    nav_fund_codes = set(codes.dropna())
    orphan_codes = nav_fund_codes - validate_fund_codes

    print(
        f"{'PASS' if not orphan_codes else 'FAIL'}: "
        f"Unknown AMFI codes: {len(orphan_codes)}"
    )

    if orphan_codes:
        print(f"Unknow codes (sample): {list(orphan_codes)[:10]}")

    print("-" * 45)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Distinct finds: {df['amfi_code'].nunique():,}")
    print(f"Distinct valid dates: {dates.nunique():,}")



def validate_aum():

    file_path = RAW_DATA_DIR / "03_aum_by_fund_house.csv"
    fund_master_path = RAW_DATA_DIR / "01_fund_master.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"AUM file not found: {file_path}")

    if not fund_master_path.exists():
        raise FileNotFoundError(f"Fund master not found: {fund_master_path}")

    df = pd.read_csv(file_path)
    funds = pd.read_csv(fund_master_path)

    print("\nDATA QUALITY REPORT: AUM BY FUND HOUSE")
    print("-" * 50)

    required_columns = ["date", "fund_house", "aum_lakh_crore", "aum_crore", "num_schemes"]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f"FAIL: Missisg columns: {missing_columns}")
        return

    print("PASS: All required columns are present")

    missing_values = df[required_columns].isna().sum()
    total_missing = int(missing_values.sum())

    if total_missing == 0:
        print("PASS: No missing values in required columns")
    else:
        print(f"FAIL: Missing valies: {total_missing}")
        print(missing_values[missing_values > 0])

    dates = pd.to_datetime(df["date"], errors="coerce")
    aum_lakh = pd.to_numeric(df["aum_lakh_crore"], errors="coerce")
    aum_crore  = pd.to_numeric(df["aum_crore"], errors="coerce")
    schemes = pd.to_numeric(df["num_schemes"], errors="coerce")

    invalid_dates = int(dates.isna().sum())
    invalid_aum_lakh = int(aum_lakh.isna().sum())
    invalid_aum_crore = int(aum_crore.isna().sum())
    invalid_schemes  =int(schemes.isna().sum())

    print(
        f"{'PASS' if invalid_dates == 0 else 'FAIL'}"
        f"Date parsing; invalid rows: {invalid_dates}"
    )
    print(
        f"{'PASS' if invalid_aum_lakh == 0 else 'FAIL'}"
        f"AUM lakh-crore numeric conversion; invalid rows: {invalid_aum_lakh}"
    )
    print(
        f"{'PASS' if invalid_aum_crore == 0 else 'FAIL'}"
        f"AUM crore numeric conversion; invalid rows: {invalid_aum_crore}"
    )
    print(
        f"{'PASS' if invalid_schemes == 0 else 'FAIL'}"
        f"Scheme-count numeric conversion; invalid rows: {invalid_schemes}"
    )

    negative_aum = int(
        ((aum_lakh < 0) | (aum_crore < 0)).sum()
    )
    negative_schemes = int((schemes < 0).sum())

    print(
        f"{'PASS' if negative_aum == 0 else 'FAIL'}: "
        f"Negative AUM records: {negative_aum}"
    )
    print(
        f"{'PASS' if negative_schemes == 0 else 'FAIL'}: "
        f"Negative scheme counts: {negative_schemes}"
    )

    fractional_schemes = int((schemes.notna() & (schemes % 1 != 0)).sum())

    print(
        f"{'PASS' if fractional_schemes == 0 else 'FAIL'}: "
        f"Fractional scheme counts: {fractional_schemes}"
    )

    key_data = pd.DataFrame({
        "fund_house": df["fund_house"].astype("string").str.strip(),
        "date": dates,
    })

    valid_keys = (
        key_data["fund_house"].notna()
        & key_data["fund_house"].ne("")
        & key_data["fund_house"].notna()
    )

    duplicate_count = int(
        key_data.loc[valid_keys].duplicated().sum()
    )

    print(
        f"{'PASS' if duplicate_count == 0 else 'FAIL'}: "
        f"Duplicate fund-house/date combinations: {duplicate_count}"
    )

    known_houses = set(
        funds["fund_house"].dropna().astype("string").str.strip()
    )
    aum_houses = set(
        df["fund_house"].dropna().astype("string").str.strip()
    )
    unknown_houses = aum_houses - known_houses

    print(
        f"{'PASS' if not unknown_houses else 'FAIL'}: "
        f"Unknown fund houses: {sorted(unknown_houses)}"
    )


    if unknown_houses:
        print(f"Unknown fund houses: {sorted(unknown_houses)}")

    expected_aum_crore = aum_lakh * 100000
    difference = (aum_crore - expected_aum_crore).abs()

    inconsistent_units = int((difference.notna() & (difference > 0.011)).sum())

    print(
        f"{'PASS' if inconsistent_units == 0 else 'FAIL'}: "
        f"AUM unit inconsistencies: {inconsistent_units}"
    )

    print("-" * 50)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Distinct fund houses: {df['fund_house'].nunique():,}")
    print(f"Distinct valid dates: {dates.nunique():,}")

if __name__ == "__main__":
    validate_fund_master()
    validate_nav_history()
    validate_aum()