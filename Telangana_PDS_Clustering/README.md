# Telangana PDS Analytics: Shop Performance Clustering and Anomaly Profiling

This project looks at about 17,000 Fair Price Shops (ration shops) of the Telangana Public Distribution System.
I join three open datasets (transactions, ration card status, shop locations) for 2023 to May 2025, explore them,
group the shops into behaviour types with **PCA and K-Means**, find unusual shops with **DBSCAN**, and show the results
in a **Streamlit** dashboard with a map.

## Files

| File / folder | What it is |
|---|---|
| `Telangana_PDS_Clustering.ipynb` | The analysis: loading, joining, EDA, features, PCA, K-Means, DBSCAN, profiling |
| `app.py` | Streamlit dashboard |
| `download_data.py` | Downloads the raw CSV files from the portal |
| `reports/Final_Report.md` | Final report with cluster insights and recommendations |
| `reports/` | Cluster profile and the list of shops to review (CSV) |
| `data/processed/` | Results of the notebook, used by the dashboard |
| `charts/` | Charts saved by the notebook |
| `data/raw/` | Raw monthly files (not uploaded to GitHub, they are about 110 MB) |

## How to run

```bash
pip install -r requirements.txt
python download_data.py
jupyter notebook Telangana_PDS_Clustering.ipynb
streamlit run app.py
```

Run the notebook first (Kernel > Restart and Run All). The dashboard reads the files it saves.
The processed results are already in the repository, so `streamlit run app.py` also works without the download.

Data pages on the Telangana Open Data Portal:
[Transactions](https://data.telangana.gov.in/dataset/telangana-state-civil-supplies-distribution-fp-shop-wise-transactions-data),
[Card status](https://data.telangana.gov.in/dataset/telangana-state-civil-supplies-distribution-fair-price-shop-card-status-data),
[FPS locations](https://data.telangana.gov.in/dataset/telangana-state-civil-supplies-distribution-fair-price-shop-status-latitude-and-longitude).

## Steps

1. Loaded the monthly files with a loop into yearly and then master tables, and joined the three tables.
2. EDA: portability trend, cards vs transactions, rice and wheat by district, seasonality.
3. Created 8 shop-level features (utilization ratio, portability share, rice per card, wheat share, volatility and more) and picked 5 for clustering.
4. Scaled the features (`StandardScaler`), used PCA for plots, K-Means with 4 clusters (elbow curve and silhouette score) and DBSCAN for noise shops.
5. Profiled the clusters, checked purity against urban/rural, and applied the clusters to policy, fraud and logistics questions.

## Results

| Result | Value |
|---|---|
| K-Means clusters | 4 (silhouette score 0.312) |
| Cluster purity (urban vs rural) | 0.941 (baseline 0.873) |
| Unusual shops found by DBSCAN | 185 (1.1%) |
| Portability share, January to May | 33.8% (2023), 35.5% (2024), 37.5% (2025) |

| Cluster | Shops | Avg cards | Utilization | Portability |
|---|---|---|---|---|
| Small Low-Volume Shops | 8,829 | 432 | 79% | 8% |
| Typical Steady Shops | 6,479 | 575 | 91% | 45% |
| Portability Hubs | 1,188 | 942 | 98% | 77% |
| Volatile Shops | 839 | 472 | 54% | 51% |

## Dashboard
* Filters for district, year and cluster
* Overview numbers and charts
* Map with shops coloured by cluster (Folium)
* Cluster profiles and the list of shops to review
* Shop search: enter a `shopNo` to compare the shop with its cluster average

## Limits
* The urban/rural label is my assumption (Hyderabad, Medchal and Ranga Reddy are urban).
* There are no confirmed fraud cases, so the flags are only leads for inspection.
* The silhouette score is modest; shop behaviour is a smooth spread rather than separate groups.
