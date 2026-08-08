CREATE OR REPLACE VIEW customer_summary AS

SELECT

Age_Group,

Income_Group,

Education,

Marital_Status,

Country,

COUNT(*) AS Total_Customers,

ROUND(AVG(Income),2) AS Average_Income,

ROUND(AVG(Total_Spend),2) AS Average_Spend,

ROUND(AVG(Total_Purchases),2) AS Average_Purchases

FROM customers

GROUP BY

Age_Group,

Income_Group,

Education,

Marital_Status,

Country;

CREATE OR REPLACE VIEW campaign_summary AS

SELECT

Age_Group,

Income_Group,

COUNT(*) AS Customers,

SUM(Response) AS Responders,

ROUND(
SUM(Response)*100.0/COUNT(*),
2
) AS Response_Rate

FROM customers

GROUP BY

Age_Group,

Income_Group;

CREATE OR REPLACE VIEW channel_summary AS

SELECT

Customer_Value,

ROUND(AVG(NumWebPurchases),2) AS Avg_Web,

ROUND(AVG(NumCatalogPurchases),2) AS Avg_Catalog,

ROUND(AVG(NumStorePurchases),2) AS Avg_Store,

ROUND(AVG(NumDealsPurchases),2) AS Avg_Deals,

ROUND(AVG(NumWebVisitsMonth),2) AS Avg_Web_Visits

FROM customers

GROUP BY Customer_Value;