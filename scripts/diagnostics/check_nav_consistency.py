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
    raise ValueError("Resolve duplicate fund-date records before calculating dailt NAV changes.")

nav["daily_change_pct"] = (nav.groupby("amfi_code")["nav"].pct_change() * 100)

print("\nDaily NAV change summary across all funds:")
print(nav["daily_change_pct"].describe(percentiles=[0.01, 0.25, 0.50, 0.75, 0.99]).round(3).to_string())

valid_changes = nav["daily_change_pct"].dropna()
largest_indices = valid_changes.abs().nlargest(10).index

print("\nLargest absolute daily changes across all funds:")

largest_changes = nav.loc[
    largest_indices,
    ["amfi_code", "date", "nav", "daily_change_pct"],
].sort_values(
    "daily_change_pct",
    key=lambda values: values.abs(),
    ascending=False,
)

largest_changes["nav"] = largest_changes["nav"].round(3)
largest_changes["daily_change_pct"] = (
    largest_changes["daily_change_pct"].round(3)
)

print(largest_changes.to_string(index=False))


print("\nCount of daily changes exceeding threshold:")
for threshold in [3, 5, 10, 20]:
    count = valid_changes.abs().gt(threshold).sum()
    print(f"Absolute change > {threshold}%: {count}")