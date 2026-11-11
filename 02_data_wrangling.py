"""Week 3 - Part 2 (ASSIGNMENT): Clean a messy dataset in Pandas -
handle missing values, filter rows, create new columns. Also: reading CSV and merging.
Run from repo root:  python python/02_data_wrangling.py
"""
import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pd.set_option("display.width", 130); pd.set_option("display.max_columns", 20)

# ---- 1. Read & inspect -----------------------------------------------------
df = pd.read_csv(f"{ROOT}/data/messy_orders.csv")
print("RAW:", df.shape)
print(df.dtypes, "\n")
print("Missing values:\n", df.isna().sum()[lambda s: s > 0], "\n")
print("Duplicate rows:", df.duplicated().sum())

# ---- 2. Standardise text ---------------------------------------------------
df["customer_name"] = df["customer_name"].str.strip().str.title()
df["city"] = df["city"].str.strip().str.title()
df["status"] = df["status"].str.strip().str.title()
df["payment_method"] = df["payment_method"].str.strip()

# ---- 3. Fix data types -----------------------------------------------------
# unit_price: "Rs 55000" / "55,000" / "55000" -> number
df["unit_price"] = (df["unit_price"].astype(str)
                    .str.replace(r"[^\d.\-]", "", regex=True)      # keep digits, dot, minus
                    .astype(float))
# order_date: two formats (YYYY-MM-DD and DD/MM/YYYY) -> datetime
df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", dayfirst=True)

# ---- 4. Remove duplicates --------------------------------------------------
n = len(df)
df = df.drop_duplicates()
print(f"\nDuplicates removed: {n - len(df)}  ({n} -> {len(df)})")

# ---- 5. Handle missing / invalid values -----------------------------------
df["payment_method"] = df["payment_method"].replace("", pd.NA).fillna("Unknown")
df["city"] = df["city"].replace("", pd.NA).fillna("Unknown")
print("Invalid (<= 0) prices:", int((df["unit_price"] <= 0).sum()))
df.loc[df["unit_price"] <= 0, "unit_price"] = pd.NA            # invalid prices -> missing
# price is a property of the product, so fill from the same product's median price
df["unit_price"] = df["unit_price"].fillna(df.groupby("product")["unit_price"].transform("median"))
# outlier: quantity above 3x the 99th-percentile-ish limit is treated as a data-entry error
limit = df["quantity"].quantile(0.75) + 3 * (df["quantity"].quantile(0.75) - df["quantity"].quantile(0.25))
print(f"Quantity outlier limit (Q3 + 3*IQR): {limit:.0f}  -> outliers:", int((df['quantity'] > limit).sum()))
df.loc[df["quantity"] > limit, "quantity"] = pd.NA
# quantity: fill with the median quantity of the same product
df["quantity"] = df["quantity"].fillna(df.groupby("product")["quantity"].transform("median")).round().astype(int)

# ---- 6. Create new columns -------------------------------------------------
df["revenue"] = df["quantity"] * df["unit_price"]
df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
df["quarter"] = "Q" + df["order_date"].dt.quarter.astype(str)
df["order_size"] = pd.cut(df["revenue"], bins=[0, 5_000, 50_000, float("inf")],
                          labels=["Small", "Medium", "Large"])

# ---- 7. Filter rows --------------------------------------------------------
delivered = df[df["status"] == "Delivered"]
big_electronics = df[(df["category"] == "Electronics") & (df["revenue"] > 50_000)]
mumbai_upi = df.query("city == 'Mumbai' and payment_method == 'UPI'")
print("\nDelivered orders:", len(delivered), "| Big electronics orders:", len(big_electronics),
      "| Mumbai UPI orders:", len(mumbai_upi))

# ---- 8. Merge with customers table ----------------------------------------
customers = pd.read_csv(f"{ROOT}/data/customers.csv")
merged = df.merge(customers, on="customer_name", how="left")
print("\nMerged shape:", merged.shape, "| rows with no customer match:", int(merged["segment"].isna().sum()))
print(merged.groupby("segment")["revenue"].sum().sort_values(ascending=False).round(0))

# ---- 9. Save & final check -------------------------------------------------
print("\nCLEAN:", merged.shape, "| missing values left:", int(merged.isna().sum().sum()))
merged.to_csv(f"{ROOT}/data/clean_orders.csv", index=False)
print(merged.head(5).to_string(index=False))
