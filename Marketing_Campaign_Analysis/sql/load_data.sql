-- =====================================================================
-- load_data.sql : load the segmented CSV into the customers table with plain SQL
-- (The notebook's section 6 does the same thing from Python - use either one.)
--
-- Before running:
--   1. Run schema.sql so that the customers table exists.
--   2. Start the MySQL client with local files enabled, for example:
--          mysql --local-infile=1 -u root -p
--      In MySQL Workbench: Edit connection > Advanced > Others > add  OPT_LOCAL_INFILE=1
--   3. Change the file path below to where marketing_segmented.csv is on your computer.
--      Use forward slashes, even on Windows.
-- =====================================================================

USE marketing_campaign_analysis;

-- Clear the table first so that running this script twice never creates duplicates
TRUNCATE TABLE customers;

LOAD DATA LOCAL INFILE 'C:/path/to/marketing_segmented.csv'
INTO TABLE customers
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    ID,
    Year_Birth,
    Education,
    Marital_Status,
    Income,
    Kidhome,
    Teenhome,
    Dt_Customer,
    Recency,
    MntWines,
    MntFruits,
    MntMeatProducts,
    MntFishProducts,
    MntSweetProducts,
    MntGoldProds,
    NumDealsPurchases,
    NumWebPurchases,
    NumCatalogPurchases,
    NumStorePurchases,
    NumWebVisitsMonth,
    AcceptedCmp3,
    AcceptedCmp4,
    AcceptedCmp5,
    AcceptedCmp1,
    AcceptedCmp2,
    Response,
    Complain,
    Country,
    Age,
    Customer_Tenure_Days,
    Customer_Tenure_Months,
    Customer_Tenure_Years,
    Children,
    Total_Spend,
    Total_Purchases,
    Campaigns_Accepted,
    @avg_spend,
    Age_Group,
    Income_Group,
    High_Income,
    Young_Customer,
    Campaign_Responder,
    High_Web_Engagement,
    Family_Customer,
    High_Spender,
    Customer_Value
)
SET
    Avg_Spend_Per_Purchase = NULLIF(@avg_spend, '');

-- Check the load: expect 56,000 customers
SELECT COUNT(*) AS customers_loaded FROM customers;
