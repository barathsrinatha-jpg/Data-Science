-- =====================================================================
-- queries.sql : analytical queries for the Marketing Campaign project
-- Every query answers one business question and is safe to run on its own.
-- Sections: A KPIs | B campaigns | C segments (CASE) | D product spend | E channels
--           F under-served | G ideal customer | H window functions | I data quality
-- =====================================================================

USE marketing_campaign_analysis;


-- =====================================================================
-- A. HEADLINE KPIs
-- =====================================================================

-- A1. Overall KPIs for the dashboard header cards
SELECT
    COUNT(*)                                AS total_customers,
    ROUND(AVG(Income), 0)                   AS avg_income,
    ROUND(AVG(Total_Spend), 0)              AS avg_total_spend,
    ROUND(AVG(Total_Purchases), 1)          AS avg_purchases,
    ROUND(AVG(NumWebVisitsMonth), 1)        AS avg_web_visits_per_month,
    ROUND(AVG(Customer_Tenure_Months), 1)   AS avg_tenure_months,
    ROUND(100 * AVG(Response), 1)           AS response_rate_pct
FROM customers;


-- =====================================================================
-- B. CAMPAIGN PERFORMANCE
-- =====================================================================

-- B1. Acceptance rate of each campaign, one row per campaign
--     (UNION ALL stacks the six measurements into one table)
SELECT 'AcceptedCmp1' AS campaign, SUM(AcceptedCmp1) AS accepted, ROUND(100 * AVG(AcceptedCmp1), 2) AS acceptance_rate_pct FROM customers
UNION ALL
SELECT 'AcceptedCmp2', SUM(AcceptedCmp2), ROUND(100 * AVG(AcceptedCmp2), 2) FROM customers
UNION ALL
SELECT 'AcceptedCmp3', SUM(AcceptedCmp3), ROUND(100 * AVG(AcceptedCmp3), 2) FROM customers
UNION ALL
SELECT 'AcceptedCmp4', SUM(AcceptedCmp4), ROUND(100 * AVG(AcceptedCmp4), 2) FROM customers
UNION ALL
SELECT 'AcceptedCmp5', SUM(AcceptedCmp5), ROUND(100 * AVG(AcceptedCmp5), 2) FROM customers
UNION ALL
SELECT 'Response (latest)', SUM(Response), ROUND(100 * AVG(Response), 2) FROM customers;

-- B2. How many campaigns did each customer accept?
SELECT
    Campaigns_Accepted,
    COUNT(*)                          AS customers,
    ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_customers,
    ROUND(AVG(Total_Spend), 0)        AS avg_spend
FROM customers
GROUP BY Campaigns_Accepted
ORDER BY Campaigns_Accepted;


-- =====================================================================
-- C. RULE-BASED SEGMENTS, BUILT WITH CASE
-- The six rules from the brief are recomputed here from the raw columns, so this
-- query also proves that the segments stored by the notebook are correct.
-- =====================================================================

-- C1. Size, response rate and spend of each rule-based segment
--     A customer can belong to several segments, so the rows overlap.
WITH flags AS (
    SELECT
        Response,
        Total_Spend,
        CASE WHEN Income > 75000                        THEN 1 ELSE 0 END AS high_income,
        CASE WHEN Age < 30                              THEN 1 ELSE 0 END AS young_customer,
        CASE WHEN Response = 1                          THEN 1 ELSE 0 END AS campaign_responder,
        CASE WHEN NumWebVisitsMonth > 5                 THEN 1 ELSE 0 END AS high_web_engagement,
        CASE WHEN Kidhome + Teenhome > 0                THEN 1 ELSE 0 END AS family_customer,
        -- top 10 percent of spenders (NTILE splits the customers into ten equal groups)
        CASE WHEN NTILE(10) OVER (ORDER BY Total_Spend) = 10 THEN 1 ELSE 0 END AS high_spender
    FROM customers
)
SELECT 'High Income (Income > 75,000)' AS segment, SUM(high_income) AS customers,
       ROUND(100 * SUM(high_income * Response) / SUM(high_income), 1) AS response_rate_pct,
       ROUND(SUM(high_income * Total_Spend) / SUM(high_income), 0)    AS avg_spend
FROM flags
UNION ALL
SELECT 'Young Customer (Age < 30)', SUM(young_customer),
       ROUND(100 * SUM(young_customer * Response) / SUM(young_customer), 1),
       ROUND(SUM(young_customer * Total_Spend) / SUM(young_customer), 0)
FROM flags
UNION ALL
SELECT 'Campaign Responder (Response = 1)', SUM(campaign_responder),
       ROUND(100 * SUM(campaign_responder * Response) / SUM(campaign_responder), 1),
       ROUND(SUM(campaign_responder * Total_Spend) / SUM(campaign_responder), 0)
FROM flags
UNION ALL
SELECT 'High Web Engagement (visits > 5)', SUM(high_web_engagement),
       ROUND(100 * SUM(high_web_engagement * Response) / SUM(high_web_engagement), 1),
       ROUND(SUM(high_web_engagement * Total_Spend) / SUM(high_web_engagement), 0)
FROM flags
UNION ALL
SELECT 'Family Customer (children > 0)', SUM(family_customer),
       ROUND(100 * SUM(family_customer * Response) / SUM(family_customer), 1),
       ROUND(SUM(family_customer * Total_Spend) / SUM(family_customer), 0)
FROM flags
UNION ALL
SELECT 'High Spender (top 10% by spend)', SUM(high_spender),
       ROUND(100 * SUM(high_spender * Response) / SUM(high_spender), 1),
       ROUND(SUM(high_spender * Total_Spend) / SUM(high_spender), 0)
FROM flags;

-- C2. Response rate by age band (the band is built with CASE from Age)
SELECT
    CASE WHEN Age < 30 THEN '1. Young (<30)'
         WHEN Age < 45 THEN '2. Adult (30-44)'
         WHEN Age < 60 THEN '3. Middle Age (45-59)'
         ELSE               '4. Senior (60+)' END AS age_band,
    COUNT(*)                                       AS customers,
    SUM(Response)                                  AS responders,
    ROUND(100 * AVG(Response), 1)                  AS response_rate_pct,
    ROUND(AVG(Total_Spend), 0)                     AS avg_spend
FROM customers
GROUP BY age_band
ORDER BY age_band;

-- C3. Response rate by income band (the top band starts at the 75,000 High Income rule)
SELECT
    CASE WHEN Income <= 30000 THEN '1. Low (<=30k)'
         WHEN Income <= 60000 THEN '2. Middle (30-60k)'
         WHEN Income <= 75000 THEN '3. Upper Middle (60-75k)'
         ELSE                      '4. High (>75k)' END AS income_band,
    COUNT(*)                                            AS customers,
    ROUND(100 * AVG(Response), 1)                       AS response_rate_pct,
    ROUND(AVG(Total_Spend), 0)                          AS avg_spend
FROM customers
GROUP BY income_band
ORDER BY income_band;

-- C4. Response rate by education, marital status and country (segment summaries)
SELECT 'Education' AS dimension, Education AS segment, COUNT(*) AS customers,
       ROUND(100 * AVG(Response), 1) AS response_rate_pct, ROUND(AVG(Total_Spend), 0) AS avg_spend
FROM customers GROUP BY Education
UNION ALL
SELECT 'Marital_Status', Marital_Status, COUNT(*), ROUND(100 * AVG(Response), 1), ROUND(AVG(Total_Spend), 0)
FROM customers GROUP BY Marital_Status
UNION ALL
SELECT 'Country', Country, COUNT(*), ROUND(100 * AVG(Response), 1), ROUND(AVG(Total_Spend), 0)
FROM customers GROUP BY Country
ORDER BY dimension, response_rate_pct DESC;


-- =====================================================================
-- D. PRODUCT SPENDING BY CUSTOMER GROUP
-- =====================================================================

-- D1. Average spend per product, by age band
SELECT
    CASE WHEN Age < 30 THEN '1. Young (<30)'
         WHEN Age < 45 THEN '2. Adult (30-44)'
         WHEN Age < 60 THEN '3. Middle Age (45-59)'
         ELSE               '4. Senior (60+)' END AS age_band,
    ROUND(AVG(MntWines), 1)        AS wines,
    ROUND(AVG(MntFruits), 1)       AS fruits,
    ROUND(AVG(MntMeatProducts), 1) AS meat,
    ROUND(AVG(MntFishProducts), 1) AS fish,
    ROUND(AVG(MntSweetProducts), 1) AS sweets,
    ROUND(AVG(MntGoldProds), 1)    AS gold
FROM customers
GROUP BY age_band
ORDER BY age_band;

-- D2. Average spend per product, by country
SELECT
    Country,
    ROUND(AVG(MntWines), 1)        AS wines,
    ROUND(AVG(MntFruits), 1)       AS fruits,
    ROUND(AVG(MntMeatProducts), 1) AS meat,
    ROUND(AVG(MntFishProducts), 1) AS fish,
    ROUND(AVG(MntSweetProducts), 1) AS sweets,
    ROUND(AVG(MntGoldProds), 1)    AS gold
FROM customers
GROUP BY Country
ORDER BY wines DESC;

-- D3. Share of total spend that each product makes up, by marital status
SELECT
    Marital_Status,
    ROUND(100 * SUM(MntWines)        / SUM(Total_Spend), 1) AS wines_pct,
    ROUND(100 * SUM(MntMeatProducts) / SUM(Total_Spend), 1) AS meat_pct,
    ROUND(100 * SUM(MntFishProducts) / SUM(Total_Spend), 1) AS fish_pct,
    ROUND(100 * (SUM(MntFruits) + SUM(MntSweetProducts) + SUM(MntGoldProds)) / SUM(Total_Spend), 1) AS other_pct
FROM customers
GROUP BY Marital_Status
ORDER BY Marital_Status;


-- =====================================================================
-- E. CHANNELS AND WEBSITE VISITS OF HIGH-VALUE CUSTOMERS
-- =====================================================================

-- E1. Customers are split into spend quartiles with NTILE(4): quartile 4 = top 25% = high value
WITH tiers AS (
    SELECT *, NTILE(4) OVER (ORDER BY Total_Spend) AS spend_quartile
    FROM customers
)
SELECT
    CASE spend_quartile WHEN 4 THEN '1. High value (top 25%)'
                        WHEN 1 THEN '3. Low value (bottom 25%)'
                        ELSE        '2. Medium value' END AS tier,
    COUNT(*)                                  AS customers,
    ROUND(AVG(NumWebPurchases), 2)            AS avg_web_purchases,
    ROUND(AVG(NumCatalogPurchases), 2)        AS avg_catalog_purchases,
    ROUND(AVG(NumStorePurchases), 2)          AS avg_store_purchases,
    ROUND(AVG(NumDealsPurchases), 2)          AS avg_deal_purchases,
    ROUND(AVG(NumWebVisitsMonth), 2)          AS avg_web_visits_per_month
FROM tiers
GROUP BY tier
ORDER BY tier;


-- =====================================================================
-- F. UNDER-SERVED CUSTOMERS: low spend, high web visits, did not respond
-- =====================================================================

-- F1. Size and profile of the group. The median spend is found with ROW_NUMBER.
WITH ranked AS (
    SELECT Total_Spend,
           ROW_NUMBER() OVER (ORDER BY Total_Spend) AS rn,
           COUNT(*) OVER ()                          AS n
    FROM customers
),
median AS (
    SELECT AVG(Total_Spend) AS median_spend
    FROM ranked
    WHERE rn IN (FLOOR((n + 1) / 2), CEIL((n + 1) / 2))
),
under_served AS (
    SELECT c.*
    FROM customers c
    CROSS JOIN median m
    WHERE c.Total_Spend < m.median_spend
      AND c.NumWebVisitsMonth > 5
      AND c.Response = 0
)
SELECT
    COUNT(*)                                            AS under_served_customers,
    ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct_of_all_customers,
    ROUND(AVG(Age), 1)                                  AS avg_age,
    ROUND(AVG(Income), 0)                               AS avg_income,
    ROUND(AVG(Children), 2)                             AS avg_children,
    ROUND(AVG(Total_Spend), 0)                          AS avg_spend,
    ROUND(AVG(NumWebVisitsMonth), 1)                    AS avg_web_visits
FROM under_served;

-- F2. Where do the under-served customers live?
SELECT Country, COUNT(*) AS under_served_customers
FROM customers
WHERE Total_Spend < (SELECT AVG(Total_Spend) FROM customers)   -- simple version: below average spend
  AND NumWebVisitsMonth > 5
  AND Response = 0
GROUP BY Country
ORDER BY under_served_customers DESC;


-- =====================================================================
-- G. THE IDEAL TARGET CUSTOMER
-- =====================================================================

-- G1. Responders versus non-responders
SELECT
    CASE WHEN Response = 1 THEN 'Responders' ELSE 'Non-responders' END AS customer_group,
    COUNT(*)                          AS customers,
    ROUND(AVG(Age), 1)                AS avg_age,
    ROUND(AVG(Income), 0)             AS avg_income,
    ROUND(AVG(Children), 2)           AS avg_children,
    ROUND(AVG(Total_Spend), 0)        AS avg_spend,
    ROUND(AVG(Total_Purchases), 1)    AS avg_purchases,
    ROUND(AVG(NumWebVisitsMonth), 1)  AS avg_web_visits,
    ROUND(AVG(Recency), 1)            AS avg_recency_days
FROM customers
GROUP BY customer_group;

-- G2. The five best-responding profiles (income band x family x age band, at least 300 customers)
SELECT
    Income_Group, Family_Customer, Age_Group,
    COUNT(*)                       AS customers,
    ROUND(100 * AVG(Response), 1)  AS response_rate_pct,
    ROUND(AVG(Total_Spend), 0)     AS avg_spend
FROM customers
GROUP BY Income_Group, Family_Customer, Age_Group
HAVING COUNT(*) >= 300
ORDER BY response_rate_pct DESC
LIMIT 5;


-- =====================================================================
-- H. WINDOW FUNCTIONS
-- =====================================================================

-- H1. Rank countries by average spend and by response rate (RANK over aggregated rows)
SELECT
    Country,
    COUNT(*)                                       AS customers,
    ROUND(AVG(Total_Spend), 0)                     AS avg_spend,
    RANK() OVER (ORDER BY AVG(Total_Spend) DESC)   AS spend_rank,
    ROUND(100 * AVG(Response), 1)                  AS response_rate_pct,
    RANK() OVER (ORDER BY AVG(Response) DESC)      AS response_rank
FROM customers
GROUP BY Country
ORDER BY spend_rank;

-- H2. The three biggest spenders in every country (ROW_NUMBER within each country)
SELECT Country, ID, Total_Spend, Income, Response, spend_rank_in_country
FROM (
    SELECT Country, ID, Total_Spend, Income, Response,
           ROW_NUMBER() OVER (PARTITION BY Country ORDER BY Total_Spend DESC, ID) AS spend_rank_in_country
    FROM customers
) ranked
WHERE spend_rank_in_country <= 3
ORDER BY Country, spend_rank_in_country;

-- H3. Pareto view: how much of the total spend comes from the top 10%, 20%, ... of customers
--     (NTILE makes the deciles, SUM() OVER adds them up as a running total)
WITH deciles AS (
    SELECT NTILE(10) OVER (ORDER BY Total_Spend DESC) AS spend_decile, Total_Spend
    FROM customers
)
SELECT
    spend_decile,
    SUM(Total_Spend)                                                      AS decile_spend,
    ROUND(100 * SUM(Total_Spend) / SUM(SUM(Total_Spend)) OVER (), 1)      AS pct_of_total_spend,
    ROUND(100 * SUM(SUM(Total_Spend)) OVER (ORDER BY spend_decile)
              / SUM(SUM(Total_Spend)) OVER (), 1)                         AS cumulative_pct
FROM deciles
GROUP BY spend_decile
ORDER BY spend_decile;

-- H4. Does response change with how long someone has been a customer?
--     LAG() compares each tenure band with the previous one
WITH tenure AS (
    SELECT
        CASE WHEN Customer_Tenure_Months < 6  THEN 1
             WHEN Customer_Tenure_Months < 12 THEN 2
             WHEN Customer_Tenure_Months < 18 THEN 3
             ELSE 4 END AS band_no,
        CASE WHEN Customer_Tenure_Months < 6  THEN '0-5 months'
             WHEN Customer_Tenure_Months < 12 THEN '6-11 months'
             WHEN Customer_Tenure_Months < 18 THEN '12-17 months'
             ELSE '18+ months' END AS tenure_band,
        Response
    FROM customers
),
rates AS (
    SELECT band_no, tenure_band, COUNT(*) AS customers, ROUND(100 * AVG(Response), 1) AS response_rate_pct
    FROM tenure
    GROUP BY band_no, tenure_band
)
SELECT
    tenure_band,
    customers,
    response_rate_pct,
    ROUND(response_rate_pct - LAG(response_rate_pct) OVER (ORDER BY band_no), 1) AS change_vs_previous_band
FROM rates
ORDER BY band_no;

-- H5. Each income group compared with the overall response rate (AVG() OVER () = overall average)
SELECT
    Income_Group,
    ROUND(100 * AVG(Response), 1)                                         AS response_rate_pct,
    ROUND(100 * AVG(AVG(Response)) OVER (), 1)                            AS simple_average_of_groups_pct,
    ROUND(100 * (SELECT AVG(Response) FROM customers), 1)                 AS overall_rate_pct,
    ROUND(100 * (AVG(Response) - (SELECT AVG(Response) FROM customers)), 1) AS points_above_overall
FROM customers
GROUP BY Income_Group
ORDER BY response_rate_pct DESC;


-- =====================================================================
-- I. DATA QUALITY CHECKS
-- =====================================================================

-- I1. Sanity checks on the loaded data (every value below should be 0)
SELECT
    COUNT(*) - COUNT(DISTINCT ID)                                AS duplicate_ids,
    SUM(Income IS NULL)                                          AS missing_income,
    SUM(Age < 18 OR Age > 100)                                   AS unrealistic_age,
    SUM(Total_Spend < 0)                                         AS negative_spend,
    SUM(Total_Spend <> MntWines + MntFruits + MntMeatProducts
                     + MntFishProducts + MntSweetProducts + MntGoldProds) AS wrong_total_spend,
    SUM(Children <> Kidhome + Teenhome)                          AS wrong_children,
    SUM((Young_Customer = 'Yes') <> (Age < 30))                  AS young_flag_mismatch,
    SUM((High_Income = 'Yes') <> (Income > 75000))               AS high_income_flag_mismatch
FROM customers;
