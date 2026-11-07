# Telangana PDS dashboard
# Run the notebook first (it creates the files in data/processed and reports), then:  streamlit run app.py

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="Telangana PDS Analytics", layout="wide")


# ---------- load the data (cached so the dashboard stays fast) ----------
@st.cache_data
def load_data():
    shops = pd.read_csv("data/processed/shop_clusters.csv")
    years = pd.read_csv("data/processed/shop_year_metrics.csv")
    monthly = pd.read_csv("data/processed/district_monthly.csv", parse_dates=["date"])
    profile = pd.read_csv("reports/cluster_profile.csv")
    return shops, years, monthly, profile


shops, years, monthly, profile = load_data()

COLORS = {"Small Low-Volume Shops": "green", "Typical Steady Shops": "blue",
          "Portability Hubs": "red", "Volatile Shops": "orange"}

# ---------- sidebar filters ----------
st.sidebar.title("Filters")
all_districts = sorted(shops["distName"].unique())
chosen_districts = st.sidebar.multiselect("District (empty = all)", all_districts)
chosen_year = st.sidebar.selectbox("Year", ["All years", 2023, 2024, 2025])
chosen_clusters = st.sidebar.multiselect("Cluster", list(COLORS), default=list(COLORS))

data = shops[shops["persona"].isin(chosen_clusters)]
if chosen_districts:
    data = data[data["distName"].isin(chosen_districts)]

# for a single year, use the numbers of that year instead of the overall numbers
if chosen_year != "All years":
    this_year = years[years["year"] == chosen_year].drop(columns="year")
    data = data.drop(columns=["avg_cards", "avg_transactions", "utilization_ratio", "portability_share"])
    data = data.merge(this_year, on=["distCode", "shopNo"])

st.title("Telangana Ration Shops Dashboard")
st.write("Shop clusters (K-Means) and unusual shops (DBSCAN). Showing: " + str(len(data)) + " shops.")

if len(data) == 0:
    st.warning("No shops match the filters.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Map", "Clusters", "Shop search"])

# ---------- tab 1: overview ----------
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Shops", len(data))
    c2.metric("Average utilization", str(round(data["utilization_ratio"].mean() * 100)) + "%")
    c3.metric("Average portability share", str(round(data["portability_share"].mean() * 100)) + "%")
    c4.metric("Unusual shops (DBSCAN)", int(data["is_noise"].sum()))

    left, right = st.columns(2)
    with left:
        counts = data["persona"].value_counts().reset_index()
        counts.columns = ["persona", "shops"]
        st.plotly_chart(px.bar(counts, x="persona", y="shops", color="persona", color_discrete_map=COLORS,
                               title="Shops per cluster"), width="stretch")
    with right:
        trend = monthly if not chosen_districts else monthly[monthly["distName"].isin(chosen_districts)]
        trend = trend.groupby("date")[["noOfTrans", "otherShopTransCnt"]].sum().reset_index()
        trend["Portability share (%)"] = 100 * trend["otherShopTransCnt"] / trend["noOfTrans"]
        st.plotly_chart(px.line(trend, x="date", y="Portability share (%)", title="Portability share by month"),
                        width="stretch")

    st.subheader("By district")
    by_district = data.groupby("distName").agg(shops=("shopNo", "count"), utilization=("utilization_ratio", "mean"),
                                               portability=("portability_share", "mean"), unusual=("is_noise", "sum"))
    st.dataframe(by_district.round(3).sort_values("portability", ascending=False))

# ---------- tab 2: map ----------
with tab2:
    st.subheader("Shops coloured by cluster")
    on_map = data[data["gps_ok"]]
    max_shops = st.slider("Maximum number of shops on the map", 500, 5000, 2000, step=500)
    if len(on_map) > max_shops:
        on_map = on_map.sample(max_shops, random_state=1)
        st.info("A random sample is shown to keep the map fast. Choose a district to see all its shops.")

    m = folium.Map(location=[on_map["latitude"].median(), on_map["longitude"].median()], zoom_start=7, tiles="OpenStreetMap")
    for _, row in on_map.iterrows():
        text = row["officeName"] + " | shop " + str(row["shopNo"]) + " | " + row["persona"]
        folium.CircleMarker([row["latitude"], row["longitude"]], radius=3, color=COLORS[row["persona"]],
                            fill=True, tooltip=text).add_to(m)
    st.write("Green = Small Low-Volume, Blue = Typical Steady, Red = Portability Hubs, Orange = Volatile")
    st_folium(m, height=550, width=1100, returned_objects=[])

# ---------- tab 3: clusters ----------
with tab3:
    st.subheader("Cluster profiles (mean of every feature)")
    st.dataframe(profile.set_index("persona").drop(columns="cluster").round(3).T)

    st.plotly_chart(px.scatter(data.sample(min(5000, len(data)), random_state=1), x="PC1", y="PC2", color="persona",
                               color_discrete_map=COLORS, opacity=0.6, title="Shops in PCA space"), width="stretch")

    st.subheader("Shops to review")
    st.write("High = DBSCAN noise and far from the cluster utilization. Medium = only one of the two. "
             "A flag is only a lead for a field visit, not proof of fraud.")
    review = data[data["review_priority"] != "Normal"].sort_values("util_z", key=abs, ascending=False)
    st.dataframe(review[["review_priority", "distName", "officeName", "shopNo", "persona", "avg_cards",
                         "utilization_ratio", "portability_share", "util_z"]].round(3))

# ---------- tab 4: shop search ----------
with tab4:
    st.subheader("Compare a shop with its cluster")
    shop_no = st.number_input("Enter a shop number (shopNo), for example 1901001", min_value=0, value=0, step=1)

    if shop_no > 0:
        found = shops[shops["shopNo"] == shop_no]
        if len(found) == 0:
            st.error("Shop not found. (Shops with less than 12 months of data are not clustered.)")
        else:
            shop = found.iloc[0]
            same_cluster = shops[shops["cluster"] == shop["cluster"]]
            st.write("**" + shop["officeName"] + ", " + shop["distName"] + "**  |  cluster: **" + shop["persona"] + "**")
            if shop["is_noise"]:
                st.error("This is an unusual shop (DBSCAN noise).")
            elif shop["review_priority"] == "Medium":
                st.warning("This shop is far from its cluster in utilization.")
            else:
                st.success("This shop behaves like the other shops in its cluster.")

            features = ["avg_cards", "avg_transactions", "utilization_ratio", "portability_share",
                        "rice_per_card", "wheat_share", "volatility_monthly", "volatility_yearly"]
            table = pd.DataFrame({"This shop": shop[features], "Cluster average": same_cluster[features].mean()})
            table["Difference %"] = 100 * (table["This shop"] - table["Cluster average"]) / table["Cluster average"]
            st.dataframe(table.round(3))
            chart_data = table.reset_index()
            chart_data["Difference %"] = chart_data["Difference %"].clip(-200, 200)
            st.plotly_chart(px.bar(chart_data, x="Difference %", y="index", orientation="h",
                                   title="How far this shop is from its cluster average (%, capped at 200)"),
                            width="stretch")
    else:
        st.info("Enter a shop number to see how it compares with the average of its cluster.")
