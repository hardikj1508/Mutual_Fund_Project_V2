
import pandas as pd


# --------------------------------------------------
# 1. Load datasets
# --------------------------------------------------

nav = pd.read_csv("data/raw/02_nav_history.csv")
performance = pd.read_csv("data/raw/07_scheme_performance.csv")
fund_master = pd.read_csv("data/raw/01_fund_master.csv")


# --------------------------------------------------
# 2. Standardize AMFI codes
# --------------------------------------------------

def normalize_amfi_code(series):
    """Normalize AMFI codes so they can be safely merged."""
    return (
        pd.to_numeric(series, errors="coerce")
        .astype("Int64")
    )


nav["amfi_code"] = normalize_amfi_code(nav["amfi_code"])
performance["amfi_code"] = normalize_amfi_code(
    performance["amfi_code"]
)
fund_master["amfi_code"] = normalize_amfi_code(
    fund_master["amfi_code"]
)


# --------------------------------------------------
# 3. Clean NAV data
# --------------------------------------------------

nav["date"] = pd.to_datetime(nav["date"], errors="coerce")
nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")

# Remove records that cannot be used to calculate returns.
nav = nav.dropna(subset=["amfi_code", "date", "nav"]).copy()
nav = nav[nav["nav"] > 0].copy()

# Sort chronologically within each fund.
nav = nav.sort_values(["amfi_code", "date"])

# Check for duplicate fund-date observations.
duplicate_count = nav.duplicated(
    subset=["amfi_code", "date"],
    keep=False,
).sum()

print("Duplicate fund-date NAV records:", duplicate_count)

if duplicate_count > 0:
    raise ValueError(
        "Duplicate AMFI code/date records found. "
        "Resolve these before calculating returns."
    )


# --------------------------------------------------
# 4. Define the comparison period
# --------------------------------------------------

latest_date = nav["date"].max()
target_date = latest_date - pd.DateOffset(years=1)

print("\nLatest NAV date:", latest_date.date())
print("One-year target date:", target_date.date())


# --------------------------------------------------
# 5. Calculate one-year annualized returns
# --------------------------------------------------

results = []

for code, group in nav.groupby("amfi_code"):
    group = group.sort_values("date")

    ending_rows = group[group["date"] <= latest_date]
    starting_rows = group[group["date"] <= target_date]

    if ending_rows.empty or starting_rows.empty:
        continue

    ending = ending_rows.iloc[-1]
    starting = starting_rows.iloc[-1]

    elapsed_days = (ending["date"] - starting["date"]).days

    if elapsed_days <= 0:
        continue

    years = elapsed_days / 365.25

    calculated_return = (
        (ending["nav"] / starting["nav"]) ** (1 / years) - 1
    ) * 100

    results.append({
        "amfi_code": code,
        "start_date": starting["date"],
        "end_date": ending["date"],
        "starting_nav": starting["nav"],
        "ending_nav": ending["nav"],
        "calculated_1yr_pct": calculated_return,
    })

calculated = pd.DataFrame(results)


# --------------------------------------------------
# 6. Compare calculated and supplied returns
# --------------------------------------------------

comparison = performance[
    ["amfi_code", "scheme_name", "return_1yr_pct"]
].copy()

comparison["return_1yr_pct"] = pd.to_numeric(
    comparison["return_1yr_pct"],
    errors="coerce",
)

comparison = comparison.merge(
    calculated,
    on="amfi_code",
    how="left",
    validate="one_to_one",
)

comparison["difference_pp"] = (
    comparison["calculated_1yr_pct"]
    - comparison["return_1yr_pct"]
)

print(
    "Funds compared:",
    comparison["calculated_1yr_pct"].notna().sum(),
)


# --------------------------------------------------
# 7. Difference summary
# --------------------------------------------------

print("\nDifference summary (percentage points):")

print(
    comparison["difference_pp"]
    .describe()
    .round(3)
    .to_string()
)


# --------------------------------------------------
# 8. Largest differences
# --------------------------------------------------

print("\nLargest absolute differences:")

comparison["abs_diff"] = comparison["difference_pp"].abs()

print(
    comparison.sort_values("abs_diff", ascending=False)[
        [
            "amfi_code",
            "scheme_name",
            "return_1yr_pct",
            "calculated_1yr_pct",
            "difference_pp",
        ]
    ]
    .head(10)
    .round(3)
    .to_string(index=False)
)


# --------------------------------------------------
# 9. Correlation
# --------------------------------------------------

print("\nCorrelation between supplied and calculated returns:")

print(
    comparison[
        ["return_1yr_pct", "calculated_1yr_pct"]
    ]
    .corr()
    .round(3)
    .to_string()
)


# --------------------------------------------------
# 10. Sample comparison
# --------------------------------------------------

print("\nComparison sample:")

print(
    comparison[
        [
            "scheme_name",
            "return_1yr_pct",
            "calculated_1yr_pct",
            "difference_pp",
        ]
    ]
    .head(15)
    .round(3)
    .to_string(index=False)
)


# --------------------------------------------------
# 11. Classify plans using the fund master
# --------------------------------------------------

print("\nRegular vs Direct plan return comparison:")

comparison = comparison.merge(
    fund_master[["amfi_code", "plan"]],
    on="amfi_code",
    how="left",
    validate="one_to_one",
)

comparison["plan_type"] = (
    comparison["plan"]
    .astype("string")
    .str.strip()
    .str.title()
)

print(
    comparison.groupby("plan_type", dropna=False)[
        ["return_1yr_pct", "calculated_1yr_pct", "difference_pp"]
    ]
    .agg(["count", "mean", "median"])
    .round(3)
    .to_string()
)


# --------------------------------------------------
# 12. Funds without a plan classification
# --------------------------------------------------

print("\nFunds with missing plan classification:")

print(
    comparison.loc[
        comparison["plan_type"].isna()
        | comparison["plan_type"].eq(""),
        [
            "amfi_code",
            "scheme_name",
            "plan",
            "return_1yr_pct",
            "calculated_1yr_pct",
            "difference_pp",
        ],
    ].to_string(index=False)
)


# --------------------------------------------------
# 13. ETF details
# --------------------------------------------------

print("\nETF scheme details from fund master:")

print(
    fund_master.loc[
        fund_master["amfi_code"].eq(118635)
    ].to_string(index=False)
)


# --------------------------------------------------
# 14. Fund identity reconciliation
# --------------------------------------------------

print("\nFund identity reconciliation:")

identity_check = (
    performance[["amfi_code", "scheme_name"]]
    .merge(
        fund_master[["amfi_code", "scheme_name"]],
        on="amfi_code",
        how="outer",
        suffixes=("_performance", "_master"),
        indicator=True,
        validate="one_to_one",
    )
)

identity_check["name_matches"] = (
    identity_check["scheme_name_performance"]
    .fillna("")
    .str.strip()
    .eq(
        identity_check["scheme_name_master"]
        .fillna("")
        .str.strip()
    )
)

print("\nMerge status:")
print(identity_check["_merge"].value_counts().to_string())

print("\nScheme name mismatches:")

print(
    identity_check.loc[
        ~identity_check["name_matches"],
        [
            "amfi_code",
            "scheme_name_performance",
            "scheme_name_master",
        ],
    ].to_string(index=False)
)


print("\nNAV endpoint date coverage:")

comparison["start_date"] = pd.to_datetime(
    comparison["start_date"]
)
comparison["end_date"] = pd.to_datetime(
    comparison["end_date"]
)

comparison["start_date_offset_days"] = (
    comparison["start_date"] - target_date
).dt.days

comparison["end_date_offset_days"] = (
    comparison["end_date"] - latest_date
).dt.days

print(
    comparison[
        [
            "start_date_offset_days",
            "end_date_offset_days",
        ]
    ]
    .describe()
    .round(2)
    .to_string()
)

print("\nFunds with the largest start-date offsets:")

print(
    comparison.assign(
        abs_start_offset=(
            comparison["start_date_offset_days"].abs()
        )
    )
    .sort_values("abs_start_offset", ascending=False)[
        [
            "amfi_code",
            "scheme_name",
            "start_date",
            "start_date_offset_days",
            "end_date",
            "end_date_offset_days",
        ]
    ]
    .head(10)
    .to_string(index=False)
)
