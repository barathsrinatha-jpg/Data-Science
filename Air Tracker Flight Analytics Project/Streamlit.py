import os

import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Air Tracker Dashboard", page_icon="✈️", layout="wide")

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PASSWORD"),
    "database": "flight_analytics",
}

DELAYED = "(status = 'Delayed' OR delay_minutes > 15)"


@st.cache_data(ttl=300, show_spinner=False)
def run_query(sql):
    """Run a SELECT against MySQL and return a DataFrame."""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
    finally:
        conn.close()
    for col in df.columns:
        if df[col].map(lambda v: type(v).__name__ == "Decimal").any():
            df[col] = pd.to_numeric(df[col].astype(float), errors="coerce")
    return df


st.title("✈️ Air Tracker Dashboard")
st.markdown("### Flight Analytics & Performance Insights")

try:
    airports_df = run_query("SELECT * FROM airport ORDER BY name")
    flights_df = run_query(
        "SELECT *, COALESCE(scheduled_departure, scheduled_arrival) AS flight_time FROM flights"
    )
    delay_df = run_query(
        """
        SELECT d.airport_iata, a.name AS airport,
               SUM(d.total_flights)    AS total_flights,
               SUM(d.delayed_flights)  AS delayed_flights,
               SUM(d.canceled_flights) AS canceled_flights,
               ROUND(100 * SUM(d.delayed_flights) / NULLIF(SUM(d.total_flights), 0), 2) AS delay_pct,
               ROUND(SUM(d.avg_delay_min * d.total_flights) / NULLIF(SUM(d.total_flights), 0), 2)
                   AS avg_delay_min
        FROM airport_delays d
        JOIN airport a ON a.iata_code = d.airport_iata
        WHERE d.source = 'flights_calc'
        GROUP BY d.airport_iata, a.name
        """
    )
except mysql.connector.Error as err:
    st.error(f"❌ Database connection failed: {err}")
    st.info("Check that the MySQL service is running and the DB_PASSWORD variable is set.")
    st.stop()

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go To",
    [
        "Homepage Dashboard",
        "Search & Filter Flights",
        "Airport Details Viewer",
        "Delay Analysis",
        "Route Leaderboards",
    ],
)

if page == "Homepage Dashboard":
    st.header("Summary Statistics")

    total_flights = len(flights_df)
    delayed = (
        (flights_df["status"] == "Delayed") | (flights_df["delay_minutes"] > 15)
    ).sum()
    avg_delay = (
        (delay_df["avg_delay_min"] * delay_df["total_flights"]).sum()
        / delay_df["total_flights"].sum()
        if len(delay_df) and delay_df["total_flights"].sum()
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Airports", len(airports_df))
    c2.metric("Total Flights Fetched", f"{total_flights:,}")
    c3.metric("Average Delay (mins)", round(float(avg_delay), 2))
    c4.metric("Delayed Flights", f"{100 * delayed / max(total_flights, 1):.1f}%")

    st.divider()
    left, right = st.columns(2)

    traffic = (
        pd.concat([flights_df["origin_iata"], flights_df["destination_iata"]])
        .value_counts()
        .reindex(airports_df["iata_code"])
        .fillna(0)
        .reset_index()
    )
    traffic.columns = ["Airport", "Flights"]
    left.subheader("Flights per Airport")
    left.plotly_chart(px.bar(traffic, x="Airport", y="Flights"), width="stretch")

    status_counts = flights_df["status"].fillna("Unknown").value_counts().reset_index()
    status_counts.columns = ["Status", "Flights"]
    right.subheader("Flights by Status")
    right.plotly_chart(px.pie(status_counts, names="Status", values="Flights"), width="stretch")

elif page == "Search & Filter Flights":
    st.header("Search & Filter Flights")

    col1, col2 = st.columns(2)
    search_flight = col1.text_input("Search Flight Number")
    search_airline = col2.text_input("Search Airline Code")

    col3, col4 = st.columns(2)
    status_filter = col3.selectbox(
        "Filter by Status", ["All"] + sorted(flights_df["status"].dropna().unique().tolist())
    )
    origin_filter = col4.selectbox(
        "Filter by Origin", ["All"] + sorted(flights_df["origin_iata"].dropna().unique().tolist())
    )

    flight_times = pd.to_datetime(flights_df["flight_time"])
    date_range = st.date_input(
        "Filter by Date Range",
        value=(flight_times.min().date(), flight_times.max().date()),
    )

    result = flights_df.copy()
    if search_flight:
        result = result[result["flight_number"].str.contains(search_flight, case=False, na=False)]
    if search_airline:
        result = result[result["airline_code"].str.contains(search_airline, case=False, na=False)]
    if status_filter != "All":
        result = result[result["status"] == status_filter]
    if origin_filter != "All":
        result = result[result["origin_iata"] == origin_filter]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        day = pd.to_datetime(result["flight_time"]).dt.date
        result = result[(day >= date_range[0]) & (day <= date_range[1])]

    st.write(f"**{len(result):,}** flights match")

    page_size = st.selectbox("Rows per page", [25, 50, 100, 500], index=1)
    pages = max(1, -(-len(result) // page_size))
    page_no = st.number_input("Page", min_value=1, max_value=pages, value=1, step=1)
    start = (page_no - 1) * page_size
    st.dataframe(result.iloc[start:start + page_size], width="stretch")

elif page == "Airport Details Viewer":
    st.header("Airport Details Viewer")

    labels = (airports_df["iata_code"] + " - " + airports_df["name"]).tolist()
    choice = st.selectbox("Select Airport", labels)
    iata = choice.split(" - ")[0]
    info = airports_df[airports_df["iata_code"] == iata].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("City / Country", f"{info['city']}, {info['country']}")
    c2.metric("Timezone", info["timezone"])
    c3.metric("Coordinates", f"{info['latitude']:.3f}, {info['longitude']:.3f}")

    st.map(pd.DataFrame({"lat": [info["latitude"]], "lon": [info["longitude"]]}), zoom=5)

    direction = st.radio("Direction", ["All", "Departures", "Arrivals"], horizontal=True)
    linked = flights_df[
        (flights_df["origin_iata"] == iata) | (flights_df["destination_iata"] == iata)
    ]
    if direction == "Departures":
        linked = linked[linked["origin_iata"] == iata]
    elif direction == "Arrivals":
        linked = linked[linked["destination_iata"] == iata]

    st.subheader(f"Linked Flights ({len(linked):,})")
    st.dataframe(
        linked[["flight_number", "airline_code", "origin_iata", "destination_iata",
                "flight_time", "status", "delay_minutes", "aircraft_model"]].head(500),
        width="stretch",
    )

elif page == "Delay Analysis":
    st.header("Delay Analysis by Airport")

    if delay_df.empty:
        st.warning("No delay data available.")
    else:
        c1, c2 = st.columns(2)
        c1.plotly_chart(
            px.bar(delay_df, x="airport_iata", y="avg_delay_min", title="Average Delay (minutes)"),
            width="stretch",
        )
        c2.plotly_chart(
            px.bar(delay_df, x="airport_iata", y="delay_pct", title="Delayed Flights (%)"),
            width="stretch",
        )
        st.plotly_chart(
            px.bar(delay_df, x="airport_iata", y="canceled_flights", title="Cancelled Flights"),
            width="stretch",
        )
        st.dataframe(delay_df.sort_values("delay_pct", ascending=False), width="stretch")

elif page == "Route Leaderboards":
    st.header("Route Leaderboards")

    st.subheader("Busiest Routes")
    routes = (
        flights_df.dropna(subset=["origin_iata", "destination_iata"])
        .groupby(["origin_iata", "destination_iata"])
        .size()
        .reset_index(name="Flights")
        .sort_values("Flights", ascending=False)
        .head(10)
    )
    st.dataframe(routes, width="stretch")
    st.plotly_chart(
        px.bar(routes.assign(Route=routes["origin_iata"] + " → " + routes["destination_iata"]),
               x="Route", y="Flights"),
        width="stretch",
    )

    st.subheader("Most Delayed Airports")
    worst = delay_df.sort_values("delay_pct", ascending=False).head(10)
    st.dataframe(worst[["airport_iata", "airport", "total_flights", "delay_pct", "avg_delay_min"]],
                 width="stretch")
