import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
file_path = r"C:\Users\barat\OneDrive\Documents\GitHub\Data-Science\Marketing_Campaign_Analysis\data\processed\marketing_feature_engineered.csv"

df = pd.read_csv(file_path)
print("=" * 60)
print("Marketing Campaign EDA")
print("=" * 60)

print(f"Rows : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nColumns")

print(df.columns)
plt.style.use("ggplot")

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10,6))

sns.histplot(
    data=df,
    x="Age",
    bins=25,
    kde=True
)

plt.title("Age Distribution")

plt.xlabel("Age")

plt.ylabel("Number of Customers")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\age_distribution.png")

plt.show()
print(df["Age"].describe())
plt.figure(figsize=(10,6))
print("\nObservation:")
print("- Most customers are between 40 and 65 years of age.")
print("- Customer concentration is highest around 45–55 years.")
print("- Very few customers are younger than 35 or older than 80.")

sns.histplot(
    data=df,
    x="Income",
    bins=30,
    kde=True
)

plt.title("Income Distribution")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\income_distribution.png")

plt.show()
print(df["Income"].describe())
plt.figure(figsize=(8,6))
print("\nObservation:")
print("- Most customers earn below ₹120,000.")
print("- A few high-income outliers are present.")
print("- Income distribution is positively skewed.")

sns.countplot(
    data=df,
    x="Education"
)

plt.xticks(rotation=45)

plt.title("Education Distribution")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\education_distribution.png")

plt.show()
plt.figure(figsize=(10,6))
print("\nObservation:")
print("- Graduation is the most common education level.")
print("- PhD customers form the second largest group.")
print("- Basic education has the lowest representation.")

sns.countplot(
    data=df,
    x="Marital_Status"
)

plt.xticks(rotation=45)

plt.title("Marital Status Distribution")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\marital_status_distribution.png")

plt.show()
plt.figure(figsize=(10,6))
print("\nObservation:")
print("- Together and Married are the largest customer groups.")
print("- YOLO and Absurd contain very few customers.")

sns.countplot(
    data=df,
    x="Country"
)

plt.xticks(rotation=45)

plt.title("Country Distribution")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\country_distribution.png")

plt.show()
plt.figure(figsize=(10,6))

print("\nObservation:")
print("- Spain has the largest customer base.")
print("- Canada is the second largest country.")
print("- Mexico has the fewest customers.")

sns.histplot(
    data=df,
    x="Total_Spend",
    bins=30,
    kde=True
)

plt.title("Total Spend Distribution")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\total_spend_distribution.png")

plt.show()
plt.figure(figsize=(10,6))

print("\nObservation:")
print("- Most customers have relatively low total spending.")
print("- A small group of customers are high spenders.")
print("- Spending distribution is positively skewed.")

sns.histplot(
    data=df,
    x="Total_Purchases",
    bins=30,
    kde=True
)

plt.title("Total Purchases Distribution")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\total_purchases_distribution.png")

plt.show()
plt.figure(figsize=(6,5))

print("\nObservation:")
print("- Most customers make around 8–18 purchases.")
print("- Very high purchase counts are uncommon.")

sns.countplot(
    data=df,
    x="Response"
)

plt.title("Campaign Response")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\response_distribution.png")

plt.show()
print("\n" + "=" * 60)
print("Bivariate Analysis")
print("=" * 60)
plt.figure(figsize=(10, 6))

print("\nObservation:")
print("- Most customers did not accept the marketing campaign.")
print("- Campaign response rate is relatively low.")

sns.scatterplot(
    data=df,
    x="Income",
    y="Total_Spend"
)

plt.title("Income vs Total Spend")
plt.xlabel("Income")
plt.ylabel("Total Spend")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\income_vs_total_spend.png")

plt.show()
plt.figure(figsize=(10, 6))

print("\nObservation:")
print("- Higher income generally corresponds to higher spending.")
print("- The relationship is positive but not perfect.")
print("- Some high-income customers spend relatively little.")

sns.scatterplot(
    data=df,
    x="Age",
    y="Total_Spend"
)

plt.title("Age vs Total Spend")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\age_vs_spend.png")

plt.show()
plt.figure(figsize=(8,6))

print("\nObservation:")
print("- No strong relationship is observed between age and total spending.")
print("- Spending occurs across nearly all age groups.")

sns.boxplot(
    data=df,
    x="Response",
    y="Income"
)

plt.title("Income vs Campaign Response")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\income_vs_response.png")

plt.show()
plt.figure(figsize=(8,6))

print("\nObservation:")
print("- Campaign responders generally have higher incomes.")
print("- Higher-income customers appear more likely to respond.")

sns.boxplot(
    data=df,
    x="Response",
    y="Age"
)

plt.title("Age vs Campaign Response")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\age_vs_response.png")

plt.show()
plt.figure(figsize=(10,6))

print("\nObservation:")
print("- Responders are slightly older on average.")
print("- Age alone does not strongly separate responders from non-responders.")

sns.boxplot(
    data=df,
    x="Education",
    y="Total_Spend"
)

plt.xticks(rotation=45)

plt.title("Education vs Total Spend")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\education_vs_spend.png")

plt.show()
plt.figure(figsize=(12,6))

print("\nObservation:")
print("- Graduation and PhD customers tend to spend more.")
print("- Basic education customers have lower overall spending.")

sns.boxplot(
    data=df,
    x="Marital_Status",
    y="Total_Spend"
)

plt.xticks(rotation=45)

plt.title("Marital Status vs Total Spend")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\marital_status_vs_spend.png")

plt.show()
plt.figure(figsize=(8,6))

print("\nObservation:")
print("- Spending differs across marital status groups.")
print("- Divorced and Widow customers show slightly higher median spending.")

sns.boxplot(
    data=df,
    x="Children",
    y="Total_Spend"
)

plt.title("Children vs Total Spend")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\children_vs_spend.png")

plt.show()
plt.figure(figsize=(10,6))

print("\nObservation:")
print("- Customers without children spend the most.")
print("- Spending generally decreases as the number of children increases.")

sns.scatterplot(
    data=df,
    x="NumWebVisitsMonth",
    y="Total_Purchases"
)

plt.title("Web Visits vs Total Purchases")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\web_visits_vs_purchases.png")

plt.show()
plt.figure(figsize=(10,6))

print("\nObservation:")
print("- Website visits do not show a strong relationship with total purchases.")
print("- More visits do not necessarily lead to more purchases.")

sns.boxplot(
    data=df,
    x="Campaigns_Accepted",
    y="Total_Spend"
)

plt.title("Campaigns Accepted vs Total Spend")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\campaigns_accepted_vs_spend.png")

plt.show()
plt.figure(figsize=(16,12))

print("\nObservation:")
print("- Customers accepting more campaigns generally spend more.")
print("- Higher campaign acceptance is associated with higher median spending.")

numeric_df = df.select_dtypes(include=["int64", "float64"])

correlation = numeric_df.corr()

sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("Correlation Heatmap")

plt.savefig("C:\\Users\\barat\\OneDrive\\Documents\\GitHub\\Data-Science\\Marketing_Campaign_Analysis\\charts\\correlation_heatmap.png")

plt.show()
print("\nObservation:")
print("- Total_Spend is strongly correlated with individual product spending.")
print("- Income has a moderate positive correlation with Total_Spend.")
print("- Purchase channels are positively related to Total_Purchases.")
print("- No strong negative correlations are observed.")