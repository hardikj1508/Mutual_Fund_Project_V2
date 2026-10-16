import pandas as pd

nav = pd.read_csv("data/raw/02_nav_history.csv")

nav["date"] = pd.to_datetime(nav["date"])
nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")

nav = nav.sort_values(["amfi_code", "date"])

summary = (
    nav.groupby("amfi_code")
    .agg(
        first_date=("date", "min"),
        first_nav=("nav", "first"),
        last_date=("date", "max"),
        last_nav=("nav", "last"),
        min_nav=("nav", "min"),
        max_nav=("nav", "max"),
        observations=("nav", "count"),
    )
    .reset_index()
)

summary["full_period_return_pct"] = (
    (summary["last_nav"] / summary["first_nav"]) - 1
) * 100

print("NAV range and full-period return by fund:")
print(
    summary.sort_values("full_period_return_pct")
    .round({
        "first_nav": 3,
        "last_nav": 3,
        "min_nav": 3,
        "max_nav": 3,
        "full_period_return_pct": 2,
    })
    .to_string(index=False)
)

print("\nFull-period return summary:")
print(
    summary["full_period_return_pct"]
    .describe()
    .round(2)
    .to_string()
)
