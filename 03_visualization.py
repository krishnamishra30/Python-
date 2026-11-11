"""Week 3 - Part 3: Intro to data visualisation with Matplotlib & Seaborn.
Run AFTER 02_data_wrangling.py (it reads data/clean_orders.csv). Charts are saved to images/.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")                       # no display needed
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f"{ROOT}/images", exist_ok=True)
df = pd.read_csv(f"{ROOT}/data/clean_orders.csv", parse_dates=["order_date"])
df = df[df["status"] == "Delivered"]
sns.set_theme(style="whitegrid")

# 1. Matplotlib bar chart: revenue by category
cat = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(cat.index, cat.values, color="#1F4E78")
ax.set_title("Revenue by Category"); ax.set_xlabel("Category"); ax.set_ylabel("Revenue (INR)")
fig.tight_layout(); fig.savefig(f"{ROOT}/images/1_revenue_by_category.png", dpi=150); plt.close(fig)

# 2. Matplotlib line chart: monthly revenue trend
monthly = df.groupby("order_month")["revenue"].sum()
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(monthly.index, monthly.values, marker="o", color="#C00000")
ax.set_title("Monthly Revenue Trend"); ax.set_xlabel("Month"); ax.set_ylabel("Revenue (INR)")
ax.tick_params(axis="x", rotation=45)
fig.tight_layout(); fig.savefig(f"{ROOT}/images/2_monthly_trend.png", dpi=150); plt.close(fig)

# 3. Seaborn barplot: average revenue per order by payment method
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(data=df, x="payment_method", y="revenue", estimator="mean", errorbar=None, ax=ax, color="#2E75B6")
ax.set_title("Average Order Revenue by Payment Method"); ax.set_ylabel("Average revenue (INR)")
fig.tight_layout(); fig.savefig(f"{ROOT}/images/3_avg_revenue_by_payment.png", dpi=150); plt.close(fig)

# 4. Seaborn histogram: distribution of order revenue
fig, ax = plt.subplots(figsize=(6, 4))
sns.histplot(df["revenue"], bins=20, ax=ax, color="#548235")
ax.set_title("Distribution of Order Revenue"); ax.set_xlabel("Revenue (INR)")
fig.tight_layout(); fig.savefig(f"{ROOT}/images/4_revenue_distribution.png", dpi=150); plt.close(fig)

# 5. Seaborn boxplot: revenue spread by category
fig, ax = plt.subplots(figsize=(6, 4))
sns.boxplot(data=df, x="category", y="revenue", ax=ax, color="#9DC3E6")
ax.set_title("Revenue Spread by Category"); ax.set_ylabel("Revenue (INR)")
fig.tight_layout(); fig.savefig(f"{ROOT}/images/5_revenue_boxplot.png", dpi=150); plt.close(fig)

# 6. Seaborn heatmap: revenue by quarter x category
pivot = df.pivot_table(index="category", columns="quarter", values="revenue", aggfunc="sum")
fig, ax = plt.subplots(figsize=(7, 4))
sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="Blues", ax=ax)
ax.tick_params(axis="y", rotation=0)
ax.set_title("Revenue: Category x Quarter")
fig.tight_layout(); fig.savefig(f"{ROOT}/images/6_heatmap_category_quarter.png", dpi=150); plt.close(fig)

print("Saved 6 charts to images/")
