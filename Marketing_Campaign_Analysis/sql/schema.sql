-- =====================================================================
-- schema.sql : database and table design for the Marketing Campaign project
-- Run order: schema.sql -> load_data.sql (or the notebook's section 6) -> views.sql -> queries.sql
-- =====================================================================

CREATE DATABASE IF NOT EXISTS marketing_campaign_analysis
    CHARACTER SET utf8mb4;

USE marketing_campaign_analysis;

-- One row per customer (ID is unique). The first 28 columns come straight from the raw file,
-- the rest are the derived features and rule-based segments built in the notebook.
-- Design notes:
--   * ID is the primary key.
--   * DECIMAL is used for money so that sums and averages are exact.
--   * Yes/No segment flags are stored as short text so they read well in dashboards.
--   * Indexes cover the columns the dashboard filters on (country, age group, income group).
CREATE TABLE IF NOT EXISTS customers (
    -- ---------- raw columns ----------
    ID                      INT PRIMARY KEY,
    Year_Birth              INT,
    Education               VARCHAR(50),
    Marital_Status          VARCHAR(50),
    Income                  DECIMAL(12,2),        -- incomes above the 99th percentile are capped
    Kidhome                 INT,
    Teenhome                INT,
    Dt_Customer             DATE,                 -- enrolment date
    Recency                 INT,                  -- days since last purchase
    MntWines                INT,
    MntFruits               INT,
    MntMeatProducts         INT,
    MntFishProducts         INT,
    MntSweetProducts        INT,
    MntGoldProds            INT,
    NumDealsPurchases       INT,
    NumWebPurchases         INT,
    NumCatalogPurchases     INT,
    NumStorePurchases       INT,
    NumWebVisitsMonth       INT,
    AcceptedCmp1            INT,
    AcceptedCmp2            INT,
    AcceptedCmp3            INT,
    AcceptedCmp4            INT,
    AcceptedCmp5            INT,
    Response                INT,                  -- accepted the latest campaign (1 = yes)
    Complain                INT,
    Country                 VARCHAR(50),

    -- ---------- derived features ----------
    Age                     INT,                  -- measured at the last enrolment date (2014-06-29)
    Customer_Tenure_Days    INT,
    Customer_Tenure_Months  DECIMAL(6,1),
    Customer_Tenure_Years   DECIMAL(6,2),
    Children                INT,                  -- Kidhome + Teenhome
    Total_Spend             DECIMAL(12,2),        -- sum of the six Mnt* columns
    Total_Purchases         INT,                  -- web + catalog + store + deals
    Campaigns_Accepted      INT,                  -- AcceptedCmp1..5
    Avg_Spend_Per_Purchase  DECIMAL(12,2),

    -- ---------- rule-based segments ----------
    Age_Group               VARCHAR(30),
    Income_Group            VARCHAR(30),
    High_Spender            VARCHAR(10),          -- Total_Spend above the 90th percentile
    Young_Customer          VARCHAR(10),          -- Age < 30
    Family_Customer         VARCHAR(10),          -- Children > 0
    Campaign_Responder      VARCHAR(10),          -- Response = 1
    High_Web_Engagement     VARCHAR(10),          -- NumWebVisitsMonth > 5
    High_Income             VARCHAR(10),          -- Income > 75,000
    Customer_Value          VARCHAR(30),          -- High / Medium / Low value by spend quartile

    INDEX idx_country      (Country),
    INDEX idx_income_group (Income_Group),
    INDEX idx_age_group    (Age_Group)
);
