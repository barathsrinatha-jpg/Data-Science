CREATE DATABASE IF NOT EXISTS marketing_campaign_analysis;

USE marketing_campaign_analysis;

CREATE TABLE IF NOT EXISTS customers (

    ID INT PRIMARY KEY,

    Year_Birth INT,

    Education VARCHAR(50),

    Marital_Status VARCHAR(50),

    Income DECIMAL(12,2),

    Kidhome INT,

    Teenhome INT,

    Dt_Customer DATE,

    Recency INT,

    MntWines INT,

    MntFruits INT,

    MntMeatProducts INT,

    MntFishProducts INT,

    MntSweetProducts INT,

    MntGoldProds INT,

    NumDealsPurchases INT,

    NumWebPurchases INT,

    NumCatalogPurchases INT,

    NumStorePurchases INT,

    NumWebVisitsMonth INT,

    AcceptedCmp1 INT,

    AcceptedCmp2 INT,

    AcceptedCmp3 INT,

    AcceptedCmp4 INT,

    AcceptedCmp5 INT,

    Response INT,

    Complain INT,

    Country VARCHAR(50),

    Age INT,

    Customer_Tenure_Days INT,

    Customer_Tenure_Years DECIMAL(6,2),

    Children INT,

    Total_Spend DECIMAL(12,2),

    Total_Purchases INT,

    Campaigns_Accepted INT,

    Age_Group VARCHAR(30),

    Income_Group VARCHAR(30),

    High_Spender VARCHAR(10),

    Family_Customer VARCHAR(10),

    Campaign_Responder VARCHAR(10),

    High_Web_Engagement VARCHAR(10),

    High_Income VARCHAR(10),

    Customer_Value VARCHAR(30)

);