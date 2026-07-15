SELECT
    COUNT(*) AS Total_Customers
FROM customers;

SELECT
    COUNT(*) AS Total_Customers,
    SUM(Response) AS Responders,
    ROUND(SUM(Response) * 100.0 / COUNT(*),2) AS Response_Rate
FROM customers;

SELECT
    ROUND(AVG(Total_Spend),2) AS Average_Total_Spend
FROM customers;

SELECT
    ROUND(AVG(Income),2) AS Average_Income
FROM customers;

SELECT
    Age_Group,
    COUNT(*) AS Customers
FROM customers
GROUP BY Age_Group
ORDER BY Customers DESC;

SELECT
    Income_Group,
    COUNT(*) AS Customers
FROM customers
GROUP BY Income_Group
ORDER BY Customers DESC;

SELECT
    Education,
    COUNT(*) AS Customers
FROM customers
GROUP BY Education
ORDER BY Customers DESC;

SELECT
    Marital_Status,
    COUNT(*) AS Customers
FROM customers
GROUP BY Marital_Status
ORDER BY Customers DESC;

SELECT
    Income_Group,
    COUNT(*) AS Customers,
    SUM(Response) AS Responders,
    ROUND(SUM(Response)*100.0/COUNT(*),2) AS Response_Rate
FROM customers
GROUP BY Income_Group
ORDER BY Response_Rate DESC;

SELECT
    Age_Group,
    ROUND(AVG(Total_Spend),2) AS Average_Spend
FROM customers
GROUP BY Age_Group
ORDER BY Average_Spend DESC;

SELECT
    Country,
    ROUND(AVG(Total_Spend),2) AS Average_Spend
FROM customers
GROUP BY Country
ORDER BY Average_Spend DESC;

SELECT
    SUM(NumWebPurchases) AS Web_Purchases,
    SUM(NumCatalogPurchases) AS Catalog_Purchases,
    SUM(NumStorePurchases) AS Store_Purchases,
    SUM(NumDealsPurchases) AS Deal_Purchases
FROM customers;

SELECT
    Customer_Value,
    ROUND(AVG(NumWebPurchases),2) AS Avg_Web,
    ROUND(AVG(NumCatalogPurchases),2) AS Avg_Catalog,
    ROUND(AVG(NumStorePurchases),2) AS Avg_Store,
    ROUND(AVG(NumDealsPurchases),2) AS Avg_Deals
FROM customers
GROUP BY Customer_Value;

SELECT
    ID,
    Income,
    Total_Spend,
    NumWebVisitsMonth,
    Response
FROM customers
WHERE
    Response = 0
    AND NumWebVisitsMonth > 5
    AND Total_Spend <
    (
        SELECT AVG(Total_Spend)
        FROM customers
    )
ORDER BY NumWebVisitsMonth DESC;

SELECT
    Age_Group,
    Income_Group,
    Education,
    Marital_Status,
    Country,
    COUNT(*) AS Responders,
    ROUND(AVG(Total_Spend),2) AS Average_Spend
FROM customers
WHERE Response = 1
GROUP BY
    Age_Group,
    Income_Group,
    Education,
    Marital_Status,
    Country
ORDER BY Responders DESC, Average_Spend DESC;