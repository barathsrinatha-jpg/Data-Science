import pandas as pd
import numpy as np
file_path = r"C:\Users\barat\OneDrive\Documents\GitHub\Data-Science\Marketing_Campaign_Analysis\data\raw\marketing_campaign_data.csv"
df = pd.read_csv(file_path)
print("=" * 60)
print("Marketing Campaign Dataset")
print("=" * 60)

print(df.head())
print("=" * 60)
print("Marketing Campaign Dataset")
print("=" * 60)

print(df.head())
print("\nShape of Dataset")

print(df.shape)
print("\nColumn Names")

print(df.columns)
print("\nData Types")

print(df.dtypes)
print("\nDataset Information")

df.info()
print("\nMissing Values")

print(df.isnull().sum())
duplicates = df.duplicated().sum()

print("\nDuplicate Rows")

print(duplicates)
print(df[df["Income"].isnull()])
median_income = df["Income"].median()

df["Income"] = df["Income"].fillna(median_income)
print(df["Income"].isnull().sum())
df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"])
print(df["Dt_Customer"].dtype)
print(df.describe())
output_path = r"C:\Users\barat\OneDrive\Documents\GitHub\Data-Science\Marketing_Campaign_Analysis\data\processed\cleaned_marketing_data.csv"

df.to_csv(output_path, index=False)
print("\n" + "=" * 60)
print("Data Cleaning Completed Successfully")
print("=" * 60)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nCleaned dataset saved successfully.")
print("\n" + "=" * 60)
print("Summary Statistics")
print("=" * 60)

print(df.describe())
numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns

for column in numeric_columns:
    negative_count = (df[column] < 0).sum()

    if negative_count > 0:
        print(f"{column}: {negative_count} negative values")
print("\nTop 10 Highest Income Values")

print(df["Income"].sort_values(ascending=False).head(10))
spending_columns = [
    "MntWines",
    "MntFruits",
    "MntMeatProducts",
    "MntFishProducts",
    "MntSweetProducts",
    "MntGoldProds"
]

print(df[spending_columns].describe())
purchase_columns = [
    "NumDealsPurchases",
    "NumWebPurchases",
    "NumCatalogPurchases",
    "NumStorePurchases",
    "NumWebVisitsMonth"
]

print(df[purchase_columns].describe())
print("\nEarliest Customer Date")

print(df["Dt_Customer"].min())

print("\nLatest Customer Date")

print(df["Dt_Customer"].max())
output_path = r"C:\Users\barat\OneDrive\Documents\GitHub\Data-Science\Marketing_Campaign_Analysis\data\processed\cleaned_marketing_data.csv"

df.to_csv(output_path, index=False)

print("\nValidated dataset saved successfully.")