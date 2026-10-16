import pandas as pd

df = pd.read_csv("data/raw/02_nav_history.csv")

df["date"] = pd.to_datetime(df["date"])
df["nav"] = pd.to_numeric(df["nav"])

fund = df[df["amfi_code"].astype(str).str.strip() == "119598"].sort_values("date")

ending = fund.iloc[-1]
ending_nav = ending["nav"]

dates_to_check = [
    "2025-05-28",
    "2025-05-29",
    "2025-05-30",
    "2025-06-02",
    "2025-06-03",
]

print("Ending date:", ending["date"].date())
print("Ending NAV:", ending_nav)
print("Supplied 1-year return: 23.39%")

print("\nStarting NAV date comparision:")

for date in dates_to_check:
    matching_rows = fund[fund["date"] == pd.Timestamp(date)]

    if matching_rows.empty:
        print(date, "- No NAV observation")
        continue

    starting = matching_rows.iloc[0]
    starting_nav = starting["nav"]

    calculated_return = (ending_nav / starting_nav - 1) * 100

    print(
        date,
        "| Starting NAV:", round(starting_nav, 4),
        "| Calculated return:", round(calculated_return, 3), "%"
    )