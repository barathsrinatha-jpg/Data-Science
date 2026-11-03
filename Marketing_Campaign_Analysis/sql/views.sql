-- =====================================================================
-- views.sql : reusable views that feed the dashboard
-- Run after the customers table is loaded. CREATE OR REPLACE makes the script safe to re-run.
-- Part 1 = the three original views (unchanged). Part 2 = new views built on the same logic as queries.sql.
-- =====================================================================

USE marketing_campaign_analysis;

-- ---------------------------------------------------------------------
-- PART 1: ORIGINAL VIEWS
-- ---------------------------------------------------------------------

-- Customer counts, income, spend and purchases for every demographic combination
CREATE OR REPLACE VIEW customer_summary AS
SELECT
    Age_Group, Income_Group, Education, Marital_Status, Country,
    COUNT(*)                        AS Total_Customers,
    ROUND(AVG(Income), 2)           AS Average_Income,
    ROUND(AVG(Total_Spend), 2)      AS Average_Spend,
    ROUND(AVG(Total_Purchases), 2)  AS Average_Purchases
FROM customers
GROUP BY Age_Group, Income_Group, Education, Marital_Status, Country;

-- Response rate for every age group x income group
CREATE OR REPLACE VIEW campaign_summary AS
SELECT
    Age_Group, Income_Group,
    COUNT(*)                            AS Customers,
    SUM(Response)                       AS Responders,
    ROUND(SUM(Response) * 100.0 / COUNT(*), 2) AS Response_Rate
FROM customers
GROUP BY Age_Group, Income_Group;

-- Average purchases per channel and website visits for each customer value tier
CREATE OR REPLACE VIEW channel_summary AS
SELECT
    Customer_Value,
    ROUND(AVG(NumWebPurchases), 2)      AS Avg_Web,
    ROUND(AVG(NumCatalogPurchases), 2)  AS Avg_Catalog,
    ROUND(AVG(NumStorePurchases), 2)    AS Avg_Store,
    ROUND(AVG(NumDealsPurchases), 2)    AS Avg_Deals,
    ROUND(AVG(NumWebVisitsMonth), 2)    AS Avg_Web_Visits
FROM customers
GROUP BY Customer_Value;


-- ---------------------------------------------------------------------
-- PART 2: NEW VIEWS
-- ---------------------------------------------------------------------

-- One-row KPI card
CREATE OR REPLACE VIEW vw_kpi_overview AS
SELECT
    COUNT(*)                                AS total_customers,
    ROUND(AVG(Income), 0)                   AS avg_income,
    ROUND(AVG(Total_Spend), 0)              AS avg_total_spend,
    ROUND(AVG(Total_Purchases), 1)          AS avg_purchases,
    ROUND(AVG(NumWebVisitsMonth), 1)        AS avg_web_visits_per_month,
    ROUND(100 * AVG(Response), 1)           AS response_rate_pct
FROM customers;

-- Acceptance rate of every campaign (one row per campaign)
CREATE OR REPLACE VIEW vw_campaign_performance AS
SELECT 'AcceptedCmp1' AS campaign, SUM(AcceptedCmp1) AS accepted, ROUND(100 * AVG(AcceptedCmp1), 2) AS acceptance_rate_pct FROM customers
UNION ALL SELECT 'AcceptedCmp2', SUM(AcceptedCmp2), ROUND(100 * AVG(AcceptedCmp2), 2) FROM customers
UNION ALL SELECT 'AcceptedCmp3', SUM(AcceptedCmp3), ROUND(100 * AVG(AcceptedCmp3), 2) FROM customers
UNION ALL SELECT 'AcceptedCmp4', SUM(AcceptedCmp4), ROUND(100 * AVG(AcceptedCmp4), 2) FROM customers
UNION ALL SELECT 'AcceptedCmp5', SUM(AcceptedCmp5), ROUND(100 * AVG(AcceptedCmp5), 2) FROM customers
UNION ALL SELECT 'Response (latest)', SUM(Response), ROUND(100 * AVG(Response), 2) FROM customers;

-- Size, response rate and spend of the five stored rule-based segments
-- (the stored Yes/No flags are used here, so the view is simple and fast)
CREATE OR REPLACE VIEW vw_segment_performance AS
SELECT 'High Income' AS segment, COUNT(*) AS customers,
       ROUND(100 * AVG(Response), 1) AS response_rate_pct, ROUND(AVG(Total_Spend), 0) AS avg_spend
FROM customers WHERE High_Income = 'Yes'
UNION ALL
SELECT 'Young Customer', COUNT(*), ROUND(100 * AVG(Response), 1), ROUND(AVG(Total_Spend), 0)
FROM customers WHERE Young_Customer = 'Yes'
UNION ALL
SELECT 'High Web Engagement', COUNT(*), ROUND(100 * AVG(Response), 1), ROUND(AVG(Total_Spend), 0)
FROM customers WHERE High_Web_Engagement = 'Yes'
UNION ALL
SELECT 'Family Customer', COUNT(*), ROUND(100 * AVG(Response), 1), ROUND(AVG(Total_Spend), 0)
FROM customers WHERE Family_Customer = 'Yes'
UNION ALL
SELECT 'High Spender', COUNT(*), ROUND(100 * AVG(Response), 1), ROUND(AVG(Total_Spend), 0)
FROM customers WHERE High_Spender = 'Yes';

-- Countries ranked by average spend and by response rate (window function RANK)
CREATE OR REPLACE VIEW vw_country_ranking AS
SELECT
    Country,
    COUNT(*)                                       AS customers,
    ROUND(AVG(Total_Spend), 0)                     AS avg_spend,
    RANK() OVER (ORDER BY AVG(Total_Spend) DESC)   AS spend_rank,
    ROUND(100 * AVG(Response), 1)                  AS response_rate_pct,
    RANK() OVER (ORDER BY AVG(Response) DESC)      AS response_rank
FROM customers
GROUP BY Country;

-- Pareto view of spend: share and running share of total spend for each spend decile
CREATE OR REPLACE VIEW vw_spend_deciles AS
SELECT
    spend_decile,
    SUM(Total_Spend)                                                  AS decile_spend,
    ROUND(100 * SUM(Total_Spend) / SUM(SUM(Total_Spend)) OVER (), 1)  AS pct_of_total_spend,
    ROUND(100 * SUM(SUM(Total_Spend)) OVER (ORDER BY spend_decile)
              / SUM(SUM(Total_Spend)) OVER (), 1)                     AS cumulative_pct
FROM (
    SELECT NTILE(10) OVER (ORDER BY Total_Spend DESC) AS spend_decile, Total_Spend
    FROM customers
) d
GROUP BY spend_decile;

-- Customers who visit the website a lot, spend little and did not respond (below-average spend version)
CREATE OR REPLACE VIEW vw_under_served_customers AS
SELECT ID, Country, Age, Income, Children, Total_Spend, NumWebVisitsMonth, Recency
FROM customers
WHERE Total_Spend < (SELECT AVG(Total_Spend) FROM customers)
  AND NumWebVisitsMonth > 5
  AND Response = 0;

-- Responders versus non-responders: the profile the next campaign should copy
CREATE OR REPLACE VIEW vw_responder_profile AS
SELECT
    CASE WHEN Response = 1 THEN 'Responders' ELSE 'Non-responders' END AS customer_group,
    COUNT(*)                          AS customers,
    ROUND(AVG(Age), 1)                AS avg_age,
    ROUND(AVG(Income), 0)             AS avg_income,
    ROUND(AVG(Children), 2)           AS avg_children,
    ROUND(AVG(Total_Spend), 0)        AS avg_spend,
    ROUND(AVG(NumWebVisitsMonth), 1)  AS avg_web_visits
FROM customers
GROUP BY customer_group;
