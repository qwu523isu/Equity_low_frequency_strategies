import os
import pandas as pd
from datetime import date, timedelta
from tiingo import TiingoClient
from nasdaq_namelist_cfg import NASDAQ_100_SYMBOLS
from tiingo_api_cfg import TIINGO_API_KEY, BASE_PATH

# Set base path and output folder
base_path = BASE_PATH
today_str = date.today().strftime("%Y-%m-%d")
output_folder = os.path.join(base_path, "Output_data", today_str, "step1_nasdaq100_historical")
os.makedirs(output_folder, exist_ok=True)

# Setup Tiingo API
client = TiingoClient({'api_key': TIINGO_API_KEY})

# Set date range (last 120 days)
end_date = date.today() - timedelta(days=1)  # End date is yesterday
start_date = end_date - timedelta(days=120)  # Start date is 120 days prior

# Fetch and combine adjusted closing prices
data = {}
skipped_log = os.path.join(output_folder, "skipped_symbols.txt")  # Log file for skipped symbols

for sym in NASDAQ_100_SYMBOLS:
    try:
        df = client.get_dataframe(
            sym,
            startDate=start_date,
            endDate=end_date,
            frequency="daily"
        )
        if df.empty or "adjClose" not in df.columns:
            with open(skipped_log, "a") as f:
                f.write(f"{sym}: Insufficient data or missing adjClose\n")
            continue
        data[sym] = df["adjClose"]
    except Exception as e:
        with open(skipped_log, "a") as f:
            f.write(f"{sym}: {e}\n")

combined = pd.DataFrame(data)

# Save adjusted closing prices
price_file = os.path.join(output_folder, f"nasdaq100_adjclose_{start_date}_{end_date}.csv")
combined.to_csv(price_file)