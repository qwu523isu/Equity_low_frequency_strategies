import os
import pandas as pd
from datetime import date

base_path = r"G:\My Drive\1_Career\Working Note\Related_Codes\Equity_low_frequency_strategies"
today_str = date.today().strftime("%Y-%m-%d")
input_folder = os.path.join(base_path, "Output_data", today_str, "step1_nasdaq100_historical")
output_folder = os.path.join(base_path, "Output_data", today_str, "step2_nasdaq100_returnrate")
os.makedirs(output_folder, exist_ok=True) 

# Load the latest Step 1 file
files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]
files.sort()
input_file = os.path.join(input_folder, files[-1])
print(f"Using input file: {input_file}")

df = pd.read_csv(input_file, index_col=0, parse_dates=True)

# Calculate return rates
returns = (df.iloc[-1] / df.iloc[0] - 1).dropna()  # Calculate 120-day returns
qqq_return = returns.get("QQQ")
if qqq_return is None:
    raise ValueError("QQQ not found. Ensure NASDAQ_100_SYMBOLS includes 'QQQ'.")

# Volatility filter
daily_returns = df.pct_change().dropna()
volatility = daily_returns.std() * (252 ** 0.5)  # Annualized volatility

# 过滤：回报率比QQQ高5%以上，波动率<50% | Filter: Returns > QQQ + 5%, volatility < 50%
filtered_returns = returns[(returns > qqq_return + 0.05) & (volatility < 0.5)]
sorted_returns = filtered_returns.sort_values(ascending=False)

print(f"QQQ return over period: {qqq_return:.2%}")

# Add benchmark comparison column
result = pd.DataFrame({
    "Return": sorted_returns,
    "Above_QQQ": sorted_returns > qqq_return
})

# Save all returns
returns_file = os.path.join(output_folder, "nasdaq100_returns_vs_qqq.csv")
result.to_csv(returns_file)

# 保存前8只股票 | Save top 8
top8 = result.head(8)
top8_file = os.path.join(output_folder, "nasdaq100_top8_vs_qqq.csv")
top8.to_csv(top8_file)
print(f"Saved top 8 returns with QQQ comparison to {top8_file}")

# Save top 15 for turnover buffer
top15 = result.head(15)
top15_file = os.path.join(output_folder, "nasdaq100_top15_vs_qqq.csv")
top15.to_csv(top15_file)
print(f"Saved top 15 returns to {top15_file}")

# Summary
above_count = result["Above_QQQ"].sum()
print(f"{above_count} out of {len(result)} stocks outperformed QQQ.")