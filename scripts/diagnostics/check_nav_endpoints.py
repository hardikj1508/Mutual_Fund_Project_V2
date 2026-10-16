from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NAV_PATH = PROJECT_ROOT / "data" / "raw" / "02_nav_history.csv"

nav = pd.read_csv(NAV_PATH)

nav["amfi_code"] = pd.to_numeric(nav["amfi_code"], errors="coerce").astype("Int64")
nav["date"] = pd.to_datetime(nav["date"], errors="coerce")
nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")

nav = nav.dropna(subset=["amfi_code", "date", "nav"]).copy()
nav = nav[nav["nav"] > 0].copy()
nav = nav.sort_values(["amfi_code", "date"])

duplicate_count = nav.duplicated(subset=["amfi_code", "date"]).sum()

print("Duplicate fund-date NAV records:", duplicate_count)

if duplicate_count:
    raise ValueError("Resolve duplicate fund-date records before calculating endpoint returns.")

latest_date = nav["date"].max()
target_date = latest_date - pd.DateOffset(years=1)

print("\nLatest NAV date:", latest_date.date())
print("One-year target date:", target_date.date())

results = []

for code, group in nav.groupby("amfi_code"):
    start_rows = group[group["date"] <= target_date]
    end_rows = group[group["date"] <= latest_date]

    if start_rows.empty or end_rows.empty:
        continue

    start = start_rows.iloc[-1]
    end = end_rows.iloc[-1]

    simple_return = (end["nav"] / start["nav"] - 1) * 100

    results.append({
        "amfi_code": code,
        "start_date": start["date"],
        "start_nav": start["nav"],
        "end_date": end["date"],
        "end_nav": end["nav"],
        "simple_endpoint_return_pct": simple_return
    })

result = pd.DataFrame(results)

print("\nFunds with negative simple endpoint returns:",
      (result["simple_endpoint_return_pct"] < 0).sum())
print("Funds with positive simple endpoint returns:",
      (result["simple_endpoint_return_pct"] > 0).sum())
print("Fund with zero simple endpoint returns:",
      (result["simple_endpoint_return_pct"] == 0).sum())

print("\nEndpoint comparison for all funds:")

endpoint_comparison = result.sort_values(
    "simple_endpoint_return_pct"
)[
    [
        "amfi_code",
        "start_date",
        "start_nav",
        "end_date",
        "end_nav",
        "simple_endpoint_return_pct"
    ]
].copy()

numeric_columns = [
    "start_nav",
    "end_nav",
    "simple_endpoint_return_pct"
]

endpoint_comparison[numeric_columns] = (endpoint_comparison[numeric_columns].round(3))

print(endpoint_comparison.to_string(index=False))