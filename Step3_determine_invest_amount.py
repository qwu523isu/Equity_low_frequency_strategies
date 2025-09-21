import os
import pandas as pd
from datetime import date, datetime

# Parameters
capital_per_investment = 7500  # Capital per investment
investment_dates = [1, 8, 15, 22]  # Monthly investment dates (weekly)

base_path = r"G:\My Drive\1_Career\Working Note\Related_Codes\Equity_low_frequency_strategies"
today_str = date.today().strftime("%Y-%m-%d")
step1_folder = os.path.join(base_path, "Output_data", today_str, "step1_nasdaq100_historical")
step2_folder = os.path.join(base_path, "Output_data", today_str, "step2_nasdaq100_returnrate")
step3_folder = os.path.join(base_path, "Output_data", today_str, "step3_investment_plan")
os.makedirs(step3_folder, exist_ok=True)  # 创建输出文件夹 | Create output folder

# 检查是否为9月30日（生成10月组合） | Check if September 30 (generate October portfolio)
is_final_day = datetime.now().month == 9 and datetime.now().day == 30

# Load Step 1 prices
files = [f for f in os.listdir(step1_folder) if f.endswith(".csv")]
files.sort()
price_file = os.path.join(step1_folder, files[-1])
prices_df = pd.read_csv(price_file, index_col=0, parse_dates=True)
latest_prices = prices_df.iloc[-1]  # 最新价格 | Most recent prices

# Load Step 2 top 8 returns
top8_file = os.path.join(step2_folder, "nasdaq100_top8_vs_qqq.csv")
top8_df = pd.read_csv(top8_file, index_col=0)
top8_tickers = [t for t in top8_df.index.tolist() if t != "QQQ"]  # 排除QQQ | Exclude QQQ

# 换手率缓冲：加载前期的top15 | Turnover buffer: Load previous top 15
prev_file = os.path.join(base_path, "Output_data", "previous_top15.csv")
if os.path.exists(prev_file):
    prev_top15 = pd.read_csv(prev_file).index.tolist()[:15]
    top8_tickers = [t for t in top8_tickers if t in prev_top15] + \
                   [t for t in top8_tickers if t not in prev_top15][: (8 - len([t for t in top8_tickers if t in prev_top15]))]

# 分配资本（允许小数股） | Allocate capital (fractional shares allowed)
allocation = capital_per_investment / len(top8_tickers)  # 每只股票分配金额 | Allocation per stock
plan = []
for ticker in top8_tickers:
    if ticker not in latest_prices:
        continue
    price = latest_prices[ticker]
    shares = allocation / price  # 计算股数 | Calculate shares
    invested = shares * price  # 投资金额 | Invested amount
    plan.append({
        "Ticker": ticker,
        "Price": price,
        "Shares": shares,
        "Invested": invested,
        "Investment_Date": today_str
    })

plan_df = pd.DataFrame(plan)

# 保存单次投资计划 | Save single investment plan
output_file = os.path.join(step3_folder, f"investment_plan_{today_str}.csv")
plan_df.to_csv(output_file, index=False)

# 如果是9月30日，合并9月所有投资 | If September 30, consolidate September investments
if is_final_day:
    all_plans = []
    for d in investment_dates:
        date_str = f"2025-09-{d:02d}"
        plan_file = os.path.join(step3_folder, f"investment_plan_{date_str}.csv")
        if os.path.exists(plan_file):
            all_plans.append(pd.read_csv(plan_file))
    if all_plans:
        combined_plan = pd.concat(all_plans).groupby("Ticker").agg({
            "Price": "last",
            "Shares": "sum",
            "Invested": "sum",
            "Investment_Date": "last"
        }).reset_index()
        combined_file = os.path.join(step3_folder, "october_portfolio.csv")
        combined_plan.to_csv(combined_file, index=False)
        print(f"Saved October portfolio to {combined_file}")

# 保存top15用于下次换手率缓冲 | Save top 15 for next turnover buffer
top15_file = os.path.join(step2_folder, "nasdaq100_top15_vs_qqq.csv")
if os.path.exists(top15_file):
    os.rename(top15_file, prev_file)

# 投资组合总结 | Portfolio summary
total_invested = plan_df["Invested"].sum()
leftover_cash = capital_per_investment - total_invested
print(plan_df)
print(f"Total invested: {total_invested:.2f}, leftover cash: {leftover_cash:.2f}")
print(f"Saved investment plan to {output_file}")