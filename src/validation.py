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

def validate_sip():

    file_path = RAW_DATA_DIR / "04_monthly_sip_inflows.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"SIP file not found: {file_path}")

    df = pd.read_csv(file_path)

    print("\nDATA QUALITY REPORT: MONTHLY SIP INFLOWS")
    print("=" * 50)

    required_columns = [
        "month",
        "sip_inflow_crore", 
        "active_sip_accounts_crore",
        "new_sip_accounts_lakh",
        "sip_aum_lakh_crore",
        "yoy_growth_pct"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        print(f"FAIL: Missing columns: {missing_columns}")
        return
    
    print("PASS: All required columns are present")

    required_fields = [
        "month",
        "sip_inflow_crore", 
        "active_sip_accounts_crore",
        "new_sip_accounts_lakh",
        "sip_aum_lakh_crore"
    ]

    missing_values = df[required_fields].isna().sum()
    total_missing = int(missing_values.sum())

    if total_missing == 0:
        print("PASS: No missing values in required fields")
    else:
        print(f"FAIL: Missing required values: {total_missing}")
        print(missing_values[missing_values > 0])

    months = pd.to_datetime(df["month"], errors="coerce")

    numeric_columns = [
        "sip_inflow_crore",
        "active_sip_accounts_crore",
        "new_sip_accounts_lakh",
        "sip_aum_lakh_crore",
        "yoy_growth_pct"
    ]

    numeric_data = {
        col: pd.to_numeric(df[col], errors="coerce")
        for col in numeric_columns
    }

    invalid_months = int(months.isna().sum())

    print(
        f"{'PASS' if invalid_months == 0 else 'FAIL'}: "
        f"Month parsing; invalid rows: {invalid_months}"
    )

    for column, values in numeric_data.items():

        invalid_count = int(values.isna().sum() - (df[column].isna().sum() if column == "yoy_growth_pct" else 0))

        print(
            f"{'PASS' if invalid_count == 0 else 'FAIL'}: "
            f"{column} numeric conversion; invalid rows: "
            f"{invalid_count}"
        )

    duplicate_months = int(months[months.notna()].duplicated().sum())

    print(
        f"{'PASS' if duplicate_months == 0 else 'FAIL' }"
        f"Duplicate months: {duplicate_months}"    
        )

    non_negative_columns = [
        "sip_inflow_crore",
        "active_sip_accounts_crore",
        "new_sip_accounts_lakh",
        "sip_aum_lakh_crore"
    ]

    for column in non_negative_columns:
        values = numeric_data[column]
        negative_count = int((values.notna() & (values < 0)).sum())

        print(
            f"{'PASS' if negative_count == 0 else 'FAIL'}: "
            f"Negative {column} values: {negative_count}"
        )

    yoy_values = numeric_data["yoy_growth_pct"]
    missing_yoy_rows = df["yoy_growth_pct"].isna()

    expected_missing_yoy = (missing_yoy_rows & months.dt.year.eq(2022))

    unexpected_missing_yoy = (missing_yoy_rows & ~months.dt.year.eq(2022))

    missing_yoy_count = int(missing_yoy_rows.sum())
    expected_count = int(expected_missing_yoy.sum())
    unexpected_count = int(unexpected_missing_yoy.sum())

    print(f"INFO: Missing YoY growth values: {missing_yoy_count}")
    print(f"INFO: Missing YoY values in 2022: {expected_count}")

    print(
        f"{'PASS' if unexpected_count == 0 else 'WARNING'}: "
        f"Missing YoY values outside 2022: {unexpected_count}"
    )

    print("-" * 50)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Distinct valid months: {months.nunique():,}")

def validate_category_inflows():
    file_path  = RAW_DATA_DIR / "05_category_inflows.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Category inflows file not found: {file_path}")

    df = pd.read_csv(file_path)

    print("\nDATA QUALITY REPORT: CATEGORY INFLOWS")
    print("=" * 50)

    required_columns = [
        "month",
        "category",
        "net_inflow_crore"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        print(f"FAIL: Missing columnsL {missing_columns}")
        return

    print("PASS: All required columns are present")

    missing_values = df[required_columns].isna().sum()
    total_missing = int(missing_values.sum())

    if total_missing == 0:
        print("PASS: No missing required columns")
    else:
        print(f"FAIL: Missing required values: {total_missing}")
        print(missing_values[missing_values > 0])

    months = pd.to_datetime(df["month"], errors="coerce")
    net_inflows = pd.to_numeric(df["net_inflow_crore"], errors="coerce")

    invalid_months = int(months.isna().sum())
    invalid_inflows = int(net_inflows.isna().sum())

    print(
        f"{'PASS' if invalid_months == 0 else 'FAIL'}: "
        f"Month parsing: invalid rows: {invalid_months}"
    )

    print(
        f"{'PASS' if invalid_inflows == 0 else 'FAIL'}: "
        f"Net inflow numeric conversion; invalid rows: {invalid_inflows}"
    )

    categories = df["category"].astype("string").str.strip()
    blank_categories = int((categories.isna() | categories.eq("")).sum())

    print(
        f"{'PASS' if blank_categories == 0 else 'FAIL'}: "
        f"Blank category values: {blank_categories}"  
    )

    key_data = pd.DataFrame({
        "month": months,

        "category": categories.str.casefold(),
    })

    valid_keys = (
        key_data["month"].notna()
        & key_data["category"].notna()
        & key_data["category"].ne("")
    )

    duplicate_count = int(
        key_data.loc[valid_keys].duplicated().sum()
    )

    print(
        f"{'PASS' if duplicate_count == 0 else 'FAIL'}: "
        f"Duplicate category-month combinations: "
        f"{duplicate_count}"
    )

    negative_count = int((net_inflows.notna() & (net_inflows < 0)).sum())

    print(f"INFO: Negative net inflow records: {negative_count}")

    print("-" * 50)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Distinct valid months: {months.nunique():,}")
    print(f"Distinct categories: {categories.nunique():,}")

def validate_folio_count():

    file_path = RAW_DATA_DIR / "06_industry_folio_count.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Folio count file not found: {file_path}")

    df = pd.read_csv(file_path)

    print("\nDATA QUALITY REPORT: INDUSTRY FOLIO COUNT")
    print("-" * 55)

    required_columns = [
        "month",
        "total_folios_crore",
        "equity_folios_crore",
        "debt_folios_crore",
        "hybrid_folios_crore",
        "others_folios_crore"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
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
        print(f"FAIL: Missing required values: {total_missing}")
        print(missing_values[missing_values > 0])

    months = pd.to_datetime(df["month"], errors="coerce")

    numeric_columns = [
        "total_folios_crore",
        "equity_folios_crore",
        "debt_folios_crore",
        "hybrid_folios_crore",
        "others_folios_crore"
    ]

    numeric_data = {
        col: pd.to_numeric(df[col], errors="coerce")
        for col in numeric_columns
    }

    invalid_months = int(months.isna().sum())

    print(
        f"{'PASS' if invalid_months == 0 else 'FAIL'}: "
        f"Month parsing; invalid rows: {invalid_months}"
    )

    for column, values in numeric_data.items():
        invalid_count = int(values.isna().sum() - df[column].isna().sum())

        print(
            f"{'PASS' if invalid_count == 0 else 'FAIL'}"
            f"{column} numeric conversion; invalid rows: "
            f"{invalid_count}"
        )

    duplicate_dates = int(months[months.notna()].duplicated().sum())

    print(
        f"{'PASS' if duplicate_dates == 0 else 'FAIL'}: "
        f"Duplicated snapshot dates: {duplicate_dates}"
    )

    for column, values in numeric_data.items():
        negative_count = int((values.notna() & (values < 0)).sum())

        print(
            f"{'PASS' if negative_count == 0 else 'FAIL'}: "
            f"Negative {column} values: {negative_count}"
        )

    print("-" * 55)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Distinct valid snapshot dates: {months.nunique():,}")
    if months.notna().any():
        print(f"First snapshot: {months.min().date()}")
        print(f"Last snapshot: {months.max().date()}")

def validate_scheme_performance():

    file_path = RAW_DATA_DIR / "07_scheme_performance.csv"
    df = pd.read_csv(file_path)

    required_columns = [
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "plan",
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
        "risk_grade"
    ]

    print("\n--- Scheme Performance Validation ---")

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print(f"FAIL: Missing columns: {missing_columns}")
    else:
        print("PASS: All required columns are present")

    if missing_columns:
        return

    if df["amfi_code"].isna().any():
        print("FAIL: Missing AMFI codes")
    else:
        print("PASS: No missing AMFI codes")

    if df["amfi_code"].duplicated().any():
        duplicate_count = df["amfi_code"].duplicated().sum()
        print(f"FAIL: {duplicate_count} duplicate AMFI codes")
    else:
        print("PASS: AMFI codes are unique")

    descriptive_fields = [
        "scheme_name",
        "fund_house",
        "category",
        "plan"
    ]

    for column in descriptive_fields:
        missing_count = df[column].isna().sum()

        if missing_count:
            print(f"FAIL: {column} has {missing_count} missing values")
        else:
            print(f"PASS: No missing values in {column}")

    numeric_fields = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
    ]

    for column in numeric_fields:
        original_missing = df[column].isna().sum()
        converted = pd.to_numeric(df[column], errors="coerce")

        invalid_count = (
            converted.isna().sum() - original_missing
        )

        if invalid_count > 0:
            print(
                f"FAIL: {column} has "
                f"{invalid_count} non-numeric values"
            )
        else:
            print(f"PASS: {column} is numeric or missing")

    fund_master_path = RAW_DATA_DIR / "01_fund_master.csv"
    fund_master = pd.read_csv(fund_master_path)

    known_codes = set(fund_master["amfi_code"].dropna().astype(str).str.strip())
    performance_codes = set(df["amfi_code"].dropna().astype(str).str.strip())
    unknown_codes = sorted(performance_codes - known_codes)

    print(f"Sample fund-master codes: {list(known_codes)[:5]}")
    print(f"Sample performance codes: {list(performance_codes)[:5]}")
    if unknown_codes:
        print(
            f"FAIL: {len(unknown_codes)} unknown AMFI codes: "
            f"{unknown_codes}"
        )
    else:
        print("PASS: All AMFI codes exists in the fund master")

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Distinct funds: {df['amfi_code'].nunique()}")

def validate_investor_transactions():

    file_path = RAW_DATA_DIR / "08_investor_transactions.csv"
    df = pd.read_csv(file_path)

    required_columns = [
        "investor_id",
        "transaction_date",
        "amfi_code",
        "transaction_type",
        "amount_inr",
        "state",
        "city",
        "city_tier",
        "age_group",
        "gender",
        "annual_income_lakh",
        "payment_mode",
        "kyc_status",
    ]
    
    print("\n--- Investor Transactions Validation ---")
    print("Note: This dataset is treated as synthetic data.")

    missing_colummns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_colummns:
        print(f"FAIL: Missing columns: {missing_colummns}")
        return

    print("PASS: All required columns are present")

    key_fields = [
        "investor_id",
        "transaction_date",
        "amfi_code",
        "transaction_type",
        "amount_inr",
    ]

    for column in key_fields:
        missing_count = df[column].isna().sum()

        if missing_count:
            print(f"FAIL: {column} has {missing_count} missing values")
        else:
            print(f"PASS: No missing values in {column}")

    parsed_dates = pd.to_datetime(df["transaction_date"], errors="coerce")
    invalid_dates = (parsed_dates.isna() & df["transaction_date"].notna()).sum()

    if invalid_dates:
        print(f"FAIL: Invalid transaction dates: {invalid_dates}")
    else:
        print("PASS: Transaction dates parse successfully")

    if parsed_dates.notna().any():
        print(f"Earliest transaction: {parsed_dates.min().date()}")
        print(f"Latest transaction: {parsed_dates.max().date()}")

    numeric_feilds = ["amount_inr", "annual_income_lakh"]

    for column in numeric_feilds:
        original_missing = df[column].isna().sum()
        converted = pd.to_numeric(df[column], errors="coerce")

        invalid_count = (converted.isna().sum() - original_missing)

        if invalid_count:
            print(
                f"FAIL: {column} has "
                f"{invalid_count} non-numeric values"
            )
        else:
            print(f"PASS: {column} is numeric or missing")

    amounts = pd.to_numeric(df["amount_inr"], errors="coerce")
    negative_amounts = (amounts < 0).sum()

    if negative_amounts:
        print(f"FAIL: Negative transaction amounts: {negative_amounts}")
    else:
        print("PASS: No negative transaction amounts")

    transaction_types = (df["transaction_type"].dropna().astype(str).str.strip().str.casefold())

    print(
        "Obsereved transaction types:",
        sorted(transaction_types.unique().tolist())
    )

    if (transaction_types == "").any():
        print("FAIL: Blank transaction types found")
    else:
        print("PASS: No blank transaction types")

    fund_master_path = RAW_DATA_DIR / "01_fund_master.csv"
    fund_master = pd.read_csv(fund_master_path)

    known_codes = set(fund_master["amfi_code"].dropna().astype(str).str.strip())
    transaction_codes = set(df["amfi_code"].dropna().astype(str).str.strip())
    unknown_codes = sorted(transaction_codes - known_codes)

    if unknown_codes:
        print(
            f"FAIL: Unknown AMFI codes ({len(unknown_codes)}): "
            f"{unknown_codes[:20]}"
        )
    else:
        print("PASS: All transactions AMFI codes exists in fund master")

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Distinct investors: {df['investor_id'].nunique()}")
    print(f"Distinct AMFI codes: {df['amfi_code'].nunique()}")
    print("Repeated investor IDs:", int(df["investor_id"].duplicated().sum()))


def validate_portfolio_holdings():
    """Validate the portfolio holdings dataset."""

    file_path = RAW_DATA_DIR / "09_portfolio_holdings.csv"
    df = pd.read_csv(file_path)

    required_columns = [
        "amfi_code",
        "stock_symbol",
        "stock_name",
        "sector",
        "weight_pct",
        "market_value_cr",
        "current_price_inr",
        "portfolio_date",
    ]

    print("\n--- Portfolio Holdings Validation ---")

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print(f"FAIL: Missing columns: {missing_columns}")
        return

    print("PASS: All required columns are present")

    # 1. Check missing values in key fields
    key_fields = [
        "amfi_code",
        "stock_symbol",
        "stock_name",
        "portfolio_date",
    ]

    for column in key_fields:
        missing_count = df[column].isna().sum()

        if missing_count:
            print(f"FAIL: {column} has {missing_count} missing values")
        else:
            print(f"PASS: No missing values in {column}")

    # 2. Validate portfolio dates
    dates = pd.to_datetime(df["portfolio_date"], errors="coerce")
    invalid_dates = (
        dates.isna() & df["portfolio_date"].notna()
    ).sum()

    if invalid_dates:
        print(f"FAIL: Invalid portfolio dates: {invalid_dates}")
    else:
        print("PASS: Portfolio dates parse successfully")

    # 3. Validate numeric fields
    numeric_fields = [
        "weight_pct",
        "market_value_cr",
        "current_price_inr",
    ]

    for column in numeric_fields:
        original_missing = df[column].isna().sum()
        converted = pd.to_numeric(df[column], errors="coerce")

        invalid_count = (
            converted.isna().sum() - original_missing
        )

        if invalid_count:
            print(
                f"FAIL: {column} has "
                f"{invalid_count} non-numeric values"
            )
        else:
            print(f"PASS: {column} is numeric or missing")

    # 4. Check negative values
    for column in numeric_fields:
        values = pd.to_numeric(df[column], errors="coerce")
        negative_count = (values < 0).sum()

        if negative_count:
            print(
                f"FAIL: {column} has "
                f"{negative_count} negative values"
            )
        else:
            print(f"PASS: No negative {column} values")

    # 5. Check portfolio weights outside 0–100%
    weights = pd.to_numeric(df["weight_pct"], errors="coerce")
    invalid_weights = ((weights < 0) | (weights > 100)).sum()

    if invalid_weights:
        print(f"FAIL: Weights outside 0–100%: {invalid_weights}")
    else:
        print("PASS: Weights are within 0–100%")

    # 6. Check duplicate fund-stock-date combinations
    duplicate_keys = df.duplicated(
        subset=["amfi_code", "stock_symbol", "portfolio_date"]
    ).sum()

    if duplicate_keys:
        print(
            "INFO: Duplicate fund-stock-date combinations: "
            f"{duplicate_keys}; investigate before deciding whether "
            "they are genuine duplicates"
        )
    else:
        print("PASS: No duplicate fund-stock-date combinations")

    # 7. Check AMFI codes against the fund master
    fund_master_path = RAW_DATA_DIR / "01_fund_master.csv"
    fund_master = pd.read_csv(fund_master_path)

    known_codes = set(
        fund_master["amfi_code"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    holding_codes = set(
        df["amfi_code"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    unknown_codes = sorted(holding_codes - known_codes)

    if unknown_codes:
        print(
            f"FAIL: Unknown AMFI codes ({len(unknown_codes)}): "
            f"{unknown_codes[:20]}"
        )
    else:
        print("PASS: All holding AMFI codes exist in fund master")

    # 8. Summary
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Distinct funds: {df['amfi_code'].nunique()}")
    print(f"Distinct stocks: {df['stock_symbol'].nunique()}")
    print(f"Distinct portfolio dates: {dates.nunique()}")

if __name__ == "__main__":
    validate_fund_master()
    validate_nav_history()
    validate_aum()
    validate_sip()
    validate_category_inflows()
    validate_folio_count()
    validate_scheme_performance()
    validate_investor_transactions()
    validate_portfolio_holdings()