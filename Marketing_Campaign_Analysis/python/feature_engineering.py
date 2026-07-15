import pandas as pd
import numpy as np
file_path = r"C:\Users\barat\OneDrive\Documents\GitHub\Data-Science\Marketing_Campaign_Analysis\data\processed\cleaned_marketing_data.csv"

df = pd.read_csv(file_path)
df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"])
print(df["Dt_Customer"].dtype)
current_year = pd.Timestamp.today().year

df["Age"] = current_year - df["Year_Birth"]
print(df[["Year_Birth", "Age"]].head())
today = pd.Timestamp.today()

df["Customer_Tenure_Days"] = (today - df["Dt_Customer"]).dt.days
df["Customer_Tenure_Years"] = (
    df["Customer_Tenure_Days"] / 365
).round(1)
print(df[["Dt_Customer", "Customer_Tenure_Years"]].head())
df["Children"] = df["Kidhome"] + df["Teenhome"]
print(df[["Kidhome", "Teenhome", "Children"]].head())
spending_columns = [
    "MntWines",
    "MntFruits",
    "MntMeatProducts",
    "MntFishProducts",
    "MntSweetProducts",
    "MntGoldProds"
]

df["Total_Spend"] = df[spending_columns].sum(axis=1)
print(df[spending_columns + ["Total_Spend"]].head())
purchase_columns = [
    "NumWebPurchases",
    "NumCatalogPurchases",
    "NumStorePurchases",
    "NumDealsPurchases"
]

df["Total_Purchases"] = df[purchase_columns].sum(axis=1)
print(df[purchase_columns + ["Total_Purchases"]].head())
campaign_columns = [
    "AcceptedCmp1",
    "AcceptedCmp2",
    "AcceptedCmp3",
    "AcceptedCmp4",
    "AcceptedCmp5"
]

df["Campaigns_Accepted"] = df[campaign_columns].sum(axis=1)
print(df[campaign_columns + ["Campaigns_Accepted"]].head())
new_columns = [
    "Age",
    "Customer_Tenure_Days",
    "Customer_Tenure_Years",
    "Children",
    "Total_Spend",
    "Total_Purchases",
    "Campaigns_Accepted"
]

print(df[new_columns].head())
output_path = r"C:\Users\barat\OneDrive\Documents\GitHub\Data-Science\Marketing_Campaign_Analysis\data\processed\marketing_feature_engineered.csv"

df.to_csv(output_path, index=False)
print("\n" + "=" * 60)
print("Feature Engineering Completed Successfully")
print("=" * 60)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nFeature-engineered dataset saved successfully.")