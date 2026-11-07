# Final Report - Telangana Ration Shop Clustering
Data used: January 2023 to May 2025

## 1. Summary
* I grouped **17,335 Fair Price Shops** in 33 districts into **4 behaviour types** (K-Means) and found **185 unusual shops** (1.1%) with DBSCAN.
* **Portability** (people collecting ration from a shop that is not their home shop) grew from 33.8% to 37.5% of all transactions (January to May, 2023 vs 2025).
* **4,114 shops** get at least half of their transactions from customers of other shops. These need extra stock.
* **9 shops** are both unusual (DBSCAN) and far from their cluster's utilization (high priority for inspection). 332 more fail one of the two tests.

## 2. Data and what I did
* **Data:** Telangana Open Data Portal: FP shop-wise transactions, card status data and FPS latitude/longitude, 2023 to May 2025.
* **Join:** transactions + card status on shopNo, distCode, month and year, then + locations on shopNo and distCode. 499,494 shop-months remain (154 of 499,648 transaction rows had no card status and were dropped).
* **Features (8):** average cards, average transactions, utilization ratio, portability share, rice per card, wheat share, monthly volatility, yearly volatility.
* **Features used for clustering (5):** average cards, utilization ratio, portability share, wheat share, monthly volatility. The other three were almost copies of these (correlation above 0.8), so they were left out of the distance calculation but are shown in the profiles.
* **Scaling:** `StandardScaler`, after taking the log of the skewed features (cards, portability).
* **Models:** PCA (for plots), K-Means with k = 4 (chosen between 4 and 5 by the silhouette score) and DBSCAN (`min_samples` 12, `eps` 1.19 from the k-distance plot).

## 3. The 4 clusters
| Persona | Shops | Avg cards | Utilization | Portability | Wheat share | Monthly volatility | Urban shops |
|---|---|---|---|---|---|---|---|
| Small Low-Volume Shops | 8,829 (51%) | 432 | 79% | 8% | 0.0% | 0.05 | 5% |
| Typical Steady Shops | 6,479 (37%) | 575 | 91% | 45% | 0.1% | 0.08 | 8% |
| Portability Hubs | 1,188 (7%) | 942 | 98% | 77% | 12.1% | 0.13 | 100% |
| Volatile Shops | 839 (5%) | 472 | 54% | 51% | 0.5% | 0.34 | 10% |

* **Typical shop:** the Small Low-Volume and Typical Steady shops (88% of all shops): few hundred cards, steady month after month.
* **Outliers:** the 185 DBSCAN noise shops. Compared with normal shops they have much lower utilization (0.57 vs 0.84), more portability (0.64 vs 0.28) and a far more unstable monthly activity (0.55 vs 0.07). 15% of the Volatile Shops are noise shops.

## 4. Evaluation
| Metric | Result |
|---|---|
| Silhouette score (k = 4) | 0.312 (k = 5: 0.284; k = 2: 0.555 but it only splits off the wheat shops) |
| Elbow curve | bends around k = 4 to 5 |
| Cluster purity (urban vs rural) | 0.941, baseline (all rural) 0.873 |
| DBSCAN noise | 185 shops (1.1%) |

The silhouette score is modest because shop behaviour changes gradually and does not form separate islands. The purity is only a little above the baseline and the gain comes almost completely from the Portability Hubs, which are 100% urban. The other clusters are 92% to 95% rural, so they are separated by behaviour and not by district type.

## 5. Business use cases
**Policy impact ("One Nation One Ration Card").** Portability share (January to May) by cluster:

| Cluster | 2023 | 2024 | 2025 | Change |
|---|---|---|---|---|
| Small Low-Volume Shops | 6.8% | 7.0% | 7.8% | +1.0 |
| Typical Steady Shops | 43.8% | 46.1% | 48.1% | +4.3 |
| Portability Hubs | 75.5% | 77.2% | 78.6% | +3.1 |
| Volatile Shops | 49.7% | 52.3% | 56.4% | +6.7 |

It grew in every cluster. In urban districts 68% of the transactions in 2025 were at a non-home shop, against 29% in rural districts.

**Fraud prevention.** A shop is flagged if its utilization is more than 3 standard deviations away from its own cluster, or if DBSCAN marks it as noise. 9 shops pass both tests (High) and 332 pass one (Medium). A flag is a reason to visit the shop, not proof of fraud.

**Logistics.** 4,114 shops have at least 50% portability, mostly in Hyderabad (627 shops, 96% of its shops), Medchal (525, 85%) and Ranga Reddy (344, 37%). The Portability Hubs cluster is concentrated around Hyderabad (97% of the mapped Hyderabad shops).

## 6. Other things I found in the EDA
* Cards and transactions are strongly linked (correlation 0.88). The average shop serves 84% of its cards each month.
* Wheat is rare: only 7.6% of shop-months have wheat, almost all in Hyderabad, Medchal and Ranga Reddy.
* There is almost no seasonality: December (1.02) is the busiest and February (0.99) the quietest compared with an average month.

## 7. Recommendations
1. **Inspect the 9 High-priority shops first**, then the 332 Medium ones (`reports/shops_to_review.csv`) instead of checking all 17,000 shops.
2. **Plan stock for the Portability Hubs by the people who really visit**, not by the registered cards.
3. **Look at the Volatile Shops** (utilization only 54%): they have a large gap between cards and transactions and an unstable month-to-month pattern.
4. **Compare shops with their own cluster**, not with the state average, because the clusters have very different normal levels (for example 8% vs 77% portability).
5. **Repeat the clustering every year** to track how the policy changes the shop behaviour.

## 8. Limits
* The portal has no urban/rural column, so I treated Hyderabad, Medchal and Ranga Reddy as urban (my assumption).
* There are no confirmed fraud cases, so the flags cannot be checked for accuracy.
* 355 of the clustered shops (2%) have a missing or wrong GPS location and are not drawn on the maps.
* Data ends in May 2025; year comparisons use January to May.
