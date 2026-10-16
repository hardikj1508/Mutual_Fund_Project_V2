import pandas as pd

nav = pd.read_csv("data/raw/02_nav_history.csv")
nav["date"] = pd.to_datetime(nav["date"], errors="coerce")
nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")
nav["amfi_code"] = nav["amfi_code"].astype(str).str.strip()

fund = (
    nav[nav["amfi_code"] == "119095"]
    .sort_values("date")
    .copy()
)

fund["daily_change_pct"] = fund["nav"].pct_change() * 100

print("First 10 observations:")
print(fund.head(10).to_string(index=False))

print("\nLast 10 observations:")
print(fund.tail(10).to_string(index=False))

print("\nObservations around the one-year target:")
target_date = fund["date"].max() - pd.DateOffset(years=1)
print("Target date:", target_date.date())

print(
    fund[
        (fund["date"] >= target_date - pd.Timedelta(days=5))
        & (fund["date"] <= target_date + pd.Timedelta(days=5))
    ].to_string(index=False)
)

print("\nLargest absolute daily NAV movements:")
largest = fund.loc[
    fund["daily_change_pct"].abs().nlargest(10).index,
    ["date", "nav", "daily_change_pct"],
]
print(largest.sort_values("daily_change_pct", key=lambda s: s.abs(), ascending=False).to_string(index=False))
