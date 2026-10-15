from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

nav = pd.read_csv(RAW_DATA_DIR / "02_nav_history.csv")
performance = pd.read_csv(RAW_DATA_DIR / "07_scheme_performance.csv")

performance["amfi_code"] = pd.to_numeric(performance["amfi_code"], errors="coerce").astype("Int64")

nav["amfi_code"] = pd.to_numeric(nav["amfi_code"], errors="coerce").astype("Int64")
nav["date"] = pd.to_datetime(nav["date"], errors="coerce")
nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")

nav = nav.dropna(subset=["amfi_code", "date", "nav"]).copy()
nav = nav[nav["nav"] > 0].copy()
nav = nav.sort_values(["amfi_code", "date"])

duplicate_count = nav.duplicated(subset=["amfi_code", "date"]).sum()

print("Duplicate find-date NAV records:", duplicate_count)

if duplicate_count:
    raise ValueError("Duplicate fund-date records must be resolved before calculating returns.")

latest_date = nav["date"].max()
target_date = latest_date - pd.DateOffset(years=3)

print("\nLatest NAV date:", latest_date.date())
print("Three-year target date:", target_date.date())

results = []

for amfi_code, group in nav.groupby("amfi_code"):
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

    calculated_return = ((ending["nav"] / starting["nav"]) ** (1 / years) - 1) * 100

    results.append({
        "amfi_code": amfi_code,
        "start_date": starting["date"],
        "end_date": ending["date"],
        "calculated_3yr_pct": calculated_return
    })

calculated = pd.DataFrame(results, columns=["amfi_code",
                                            "start_date",
                                            "end_date",
                                            "calculated_3yr_pct"])

if performance["amfi_code"].duplicated().any():
    raise ValueError(
        "Duplicated AMFI codes found in performance data."
    )

comparison = performance[["amfi_code", "scheme_name", "return_3yr_pct"]].copy()

comparison["return_3yr_pct"] = pd.to_numeric(
    comparison["return_3yr_pct"], errors="coerce"
)

comparison = comparison.merge(
    calculated,
    on="amfi_code",
    how="left",
    validate="one_to_one",
    indicator=True
)

print("\nMerge coverage:")
print(comparison["_merge"].value_counts().to_string())
print(
    "Funds with calculated returns:",
    comparison["calculated_3yr_pct"].notna().sum()
)

comparison["difference_pp"] = (comparison["calculated_3yr_pct"] - comparison["return_3yr_pct"])

print("\nThree-year difference summary (percentage points):")
print(comparison["difference_pp"].describe().round(3).to_string())

print("\nCorrelation between supplied and calculated returns:")
print(
    comparison[
        ["return_3yr_pct", "calculated_3yr_pct"]
    ].corr().round(3).to_string()
)

print("\nLargest absolute differences:")
print(
    comparison.assign(
        abs_difference=comparison["difference_pp"].abs()
    ).sort_values("abs_difference", ascending=False)[
        [
            "amfi_code",
            "scheme_name",
            "return_3yr_pct",
            "calculated_3yr_pct",
            "difference_pp"
        ]
    ].head(10).round(3).to_string(index=False)
)

comparison["start_date_offset_days"] = (comparison["start_date"] - target_date).dt.days
comparison["end_date_offset_days"] = (comparison["end_date"] - latest_date).dt.days

print("\nEndpoint date offsets (days):")
print(comparison[
    ["start_date_offset_days", "end_date_offset_days"]
].describe().round(2).to_string())