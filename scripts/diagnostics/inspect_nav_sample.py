
import pandas as pd

nav = pd.read_csv("data/raw/02_nav_history.csv")

nav["date"] = pd.to_datetime(nav["date"])
nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")

fund_code = 119551

fund_nav = (
    nav.loc[nav["amfi_code"] == fund_code]
    .sort_values("date")
    .reset_index(drop=True)
)

print("Fund NAV history:")
print("Rows:", len(fund_nav))
print("First date:", fund_nav["date"].min().date())
print("Last date:", fund_nav["date"].max().date())

print("\nNAV records around the one-year target date:")
print(
    fund_nav.loc[
        fund_nav["date"].between("2025-05-26", "2025-06-03"),
        ["date", "nav"],
    ].to_string(index=False)
)

print("\nNAV records around the latest date:")
print(
    fund_nav.loc[
        fund_nav["date"].between("2026-05-25", "2026-05-29"),
        ["date", "nav"],
    ].to_string(index=False)
)


fund_nav["daily_change_pct"] = (
    fund_nav["nav"].pct_change() * 100
)

print("\nLargest daily NAV changes:")
print(
    fund_nav.loc[
        fund_nav["daily_change_pct"].abs().nlargest(10).index,
        ["date", "nav", "daily_change_pct"],
    ]
    .sort_values("daily_change_pct")
    .round(3)
    .to_string(index=False)
)
