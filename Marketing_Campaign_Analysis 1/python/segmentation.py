import pandas as pd
import numpy as np
file_path = r"C:\Users\barat\OneDrive\Documents\GitHub\Data-Science\Marketing_Campaign_Analysis\data\processed\marketing_feature_engineered.csv"

df = pd.read_csv(file_path)
age_bins = [0, 30, 45, 60, 100]

age_labels = [
    "Young",
    "Middle Age",
    "Senior",
    "Elder"
]

df["Age_Group"] = pd.cut(
    df["Age"],
    bins=age_bins,
    labels=age_labels
)
print(df["Age_Group"].value_counts())
income_bins = [
    0,
    30000,
    60000,
    90000,
    df["Income"].max()
]

income_labels = [
    "Low Income",
    "Middle Income",
    "Upper Middle",
    "High Income"
]

df["Income_Group"] = pd.cut(
    df["Income"],
    bins=income_bins,
    labels=income_labels,
    include_lowest=True
)
high_spend = df["Total_Spend"].quantile(0.90)

df["High_Spender"] = np.where(
    df["Total_Spend"] >= high_spend,
    "Yes",
    "No"
)
df["Family_Customer"] = np.where(
    df["Children"] > 0,
    "Yes",
    "No"
)
df["Campaign_Responder"] = np.where(
    df["Response"] == 1,
    "Yes",
    "No"
)
df["High_Web_Engagement"] = np.where(
    df["NumWebVisitsMonth"] > 5,
    "Yes",
    "No"
)
df["High_Income"] = np.where(
    df["Income"] > 75000,
    "Yes",
    "No"
)
q1 = df["Total_Spend"].quantile(0.25)
q3 = df["Total_Spend"].quantile(0.75)

def customer_value(spend):

    if spend >= q3:
        return "High Value"

    elif spend >= q1:
        return "Medium Value"

    else:
        return "Low Value"

df["Customer_Value"] = df["Total_Spend"].apply(customer_value)
segment_columns = [
    "Age_Group",
    "Income_Group",
    "High_Spender",
    "Family_Customer",
    "Campaign_Responder",
    "High_Web_Engagement",
    "High_Income",
    "Customer_Value"
]

print(df[segment_columns].head())
for column in segment_columns:

    print("\n" + "=" * 50)

    print(column)

    print("=" * 50)

    print(df[column].value_counts())
output_path = r"C:\Users\barat\OneDrive\Documents\GitHub\Data-Science\Marketing_Campaign_Analysis\data\processed\marketing_segmented.csv"

df.to_csv(output_path, index=False)

print("\nSegmentation completed successfully.")