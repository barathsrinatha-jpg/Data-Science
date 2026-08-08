# 📊 Marketing Campaign Analysis

## 📌 Project Overview

The **Marketing Campaign Analysis** project is an end-to-end Data Analytics solution developed using **Python, MySQL, and Power BI**. The objective is to analyze customer demographics, purchasing behavior, campaign performance, and customer segments to generate actionable business insights for marketing decision-making.

The project follows a complete analytics workflow, including data cleaning, feature engineering, exploratory data analysis (EDA), customer segmentation, SQL analytics, and interactive dashboard development.

---

# 🎯 Business Objectives

This project aims to answer the following business questions:

- Which customer segments have the highest campaign response rate?
- How do spending patterns vary across different customer demographics?
- Which purchase channels are preferred by customers?
- Who are the company's high-value customers?
- Which customers are under-served and require targeted marketing?
- What characteristics define the ideal target customer?

---

# 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Data Cleaning, Feature Engineering & EDA |
| Pandas | Data Manipulation |
| NumPy | Numerical Operations |
| Matplotlib | Data Visualization |
| Seaborn | Statistical Visualization |
| MySQL | Database Design & SQL Analytics |
| SQLAlchemy | Data Loading into MySQL |
| Power BI | Interactive Dashboard |
| VS Code | Development Environment |

---

# 📂 Project Structure

```text
Marketing_Campaign_Analysis/
│
├── data/
│   ├── raw/
│   │   └── marketing_data.csv
│   │
│   └── processed/
│       ├── marketing_cleaned.csv
│       ├── marketing_feature_engineered.csv
│       └── marketing_segmented.csv
│
├── python/
│   ├── cleaning.py
│   ├── feature_engineering.py
│   ├── eda.py
│   ├── segmentation.py
│   └── load_to_mysql.py
│
├── sql/
│   ├── schema.sql
│   ├── load_data.sql
│   ├── queries.sql
│   └── views.sql
│
├── charts/
│
├── reports/
│   └── eda_observations.md
│
├── powerbi/
│   └── Marketing_Campaign_Analysis.pbix
│
├── README.md
└── requirements.txt
```

---

# 🔄 Project Workflow

## Phase 1 – Project Setup

- Project folder organization
- Environment setup
- Package installation

---

## Phase 2 – Data Understanding

- Dataset exploration
- Missing value analysis
- Data type validation
- Statistical summary

---

## Phase 3 – Data Cleaning

- Missing value treatment
- Duplicate removal
- Data type conversion
- Outlier inspection

---

## Phase 4 – Feature Engineering

Created new business features including:

- Age
- Customer Tenure
- Children
- Total Spend
- Total Purchases
- Campaigns Accepted

---

## Phase 5 – Exploratory Data Analysis

### Univariate Analysis

- Age Distribution
- Income Distribution
- Education Distribution
- Marital Status Distribution
- Country Distribution
- Spending Distribution
- Purchase Distribution
- Campaign Response

### Bivariate Analysis

- Income vs Total Spend
- Age vs Spending
- Education vs Spending
- Marital Status vs Spending
- Country vs Spending
- Campaign Response Analysis
- Purchase Behaviour

---

## Phase 6 – Customer Segmentation

Customers were segmented into:

- Age Group
- Income Group
- Customer Value
- High Income Customers
- High Spenders
- Family Customers
- High Web Engagement
- Campaign Responders

---

## Phase 7 – MySQL Database

- Database Design
- Table Creation
- Automated Data Loading using SQLAlchemy
- Data Validation

---

## Phase 8 – SQL Analytics

Business-oriented SQL queries were developed to analyze:

- Customer KPIs
- Demographic Analysis
- Spending Behaviour
- Campaign Performance
- Purchase Channels
- Customer Segmentation
- Strategic Business Insights

---

## Phase 9 – Power BI Dashboard

Interactive dashboard consisting of five report pages:

### 📈 Executive Dashboard

- Customer KPIs
- Customer Distribution
- Demographic Overview

---

### 👥 Customer Analysis

- Age Groups
- Income Groups
- Education
- Marital Status
- Customer Value

---

### 💰 Spending Analysis

- Product Category Spending
- Average Spend
- Country-wise Spending
- Top Spending Customers

---

### 📣 Campaign Analysis

- Campaign Response Rate
- Response by Customer Segment
- Purchase Channel Analysis
- Web Engagement

---

### 🎯 Customer Segmentation

- High Value Customers
- High Income Customers
- Family Customers
- Under-served Customers
- Business Recommendations

---

# 📊 Dashboard Features

- KPI Cards
- Clustered Bar Charts
- Column Charts
- Donut Charts
- Tables
- Matrix Visuals
- Interactive Slicers
- Cross Filtering

---

# 📈 Key Insights

- Customer spending increases with higher income levels.
- Campaign response varies significantly across customer segments.
- Store and web purchases contribute the highest purchase volume.
- High-value customers represent a relatively small portion of the customer base while contributing significantly to revenue.
- Under-served customers exhibit high website engagement but low spending and low campaign response, indicating opportunities for targeted marketing.

---

# 💼 Business Recommendations

- Prioritize high-value customers for premium marketing campaigns.
- Develop personalized campaigns for high-income customer segments.
- Increase engagement among under-served customers through targeted offers.
- Focus promotional strategies on the most effective purchase channels.
- Improve campaign personalization based on customer demographics and spending behavior.

---

# 📚 Skills Demonstrated

- Data Cleaning
- Data Wrangling
- Feature Engineering
- Exploratory Data Analysis
- Customer Segmentation
- SQL Query Development
- Relational Database Design
- Data Visualization
- Business Intelligence
- Dashboard Development
- Business Insight Generation

---

# 👨‍💻 Author

**Barath Srinath A**

Data Analytics | Business Intelligence | Python | SQL | Power BI

---

# ⭐ If you found this project useful, consider giving it a star!