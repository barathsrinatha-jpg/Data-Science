import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="Air Tracker Dashboard",
    page_icon="\u2708\ufe0f",
    layout="wide"
)

st.title("\u2708\ufe0f Air Tracker Dashboard")
st.markdown("### Flight Analytics & Performance Insights")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Barium@29893",
        database="flight_analytics"
    )

    cursor = conn.cursor()

    #st.success("\u2705 Successfully Connected to MySQL Database \ud83c\udf89")

except mysql.connector.Error as err:
    st.error(f"\u274c Database Connection Failed: {err}")

@st.cache_data
def load_airports():
    query = """
    SELECT
        a.*,
        b.delay_date,
        b.total_flights,
        b.delayed_flights,
        b.avg_delay_min,
        b.median_delay_min,
        b.canceled_flights

    FROM airport a

    LEFT JOIN airport_delays b
        ON a.iata_code = b.airport_iata
    """

    return pd.read_sql(query, conn)

@st.cache_data
def load_flights():
    query = "SELECT * FROM flights"
    return pd.read_sql(query, conn)

airports_df = load_airports()
flights_df = load_flights()

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go To",
    [
        "Homepage Dashboard",
        "Search & Filter Flights",
        "Airport Details Viewer",
        "Delay Analysis",
        "Route Leaderboards"
    ]
)

if page == "Homepage Dashboard":

    st.header("Summary Statistics")

    total_airports = airports_df["iata_code"].nunique()
    total_flights = len(flights_df)
    avg_delay = airports_df["avg_delay_min"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Airports", total_airports)
    col2.metric("Total Flights Fetched", total_flights)
    col3.metric("Average Delay (mins)", round(avg_delay, 2))

    st.divider()

    st.subheader("Flights per Airport")
    flights_per_airport = flights_df.groupby("origin_iata").size().reset_index(name="Flights")
    fig = px.bar(flights_per_airport, x="origin_iata", y="Flights")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Search & Filter Flights":

    st.header("Search & Filter Flights")

    col1, col2 = st.columns(2)

    search_flight = col1.text_input("Search Flight Number")
    search_airline = col2.text_input("Search Airline")

    status_filter = st.selectbox(
        "Filter by Status",
        ["All"] + sorted(flights_df["status"].dropna().unique().tolist())
    )

    origin_filter = st.selectbox(
        "Filter by Origin",
        ["All"] + sorted(flights_df["origin_iata"].dropna().unique().tolist())
    )

    date_range = st.date_input(
        "Filter by Date Range",
        []
    )

    filtered_df = flights_df.copy()

    if search_flight:
        filtered_df = filtered_df[
            filtered_df["flight_number"].str.contains(search_flight, case=False, na=False)
        ]

    if search_airline:
        filtered_df = filtered_df[
            filtered_df["airline_code"].str.contains(search_airline, case=False, na=False)
        ]

    if status_filter != "All":
        filtered_df = filtered_df[
            filtered_df["status"] == status_filter
        ]

    if origin_filter != "All":
        filtered_df = filtered_df[
            filtered_df["origin_iata"] == origin_filter
        ]

    filtered_df["actual_departure"] = pd.to_datetime(
        filtered_df["actual_departure"],
        utc=True,
        errors="coerce"
    )

    if len(date_range) == 2:

        start_date, end_date = date_range

        filtered_df = filtered_df[
            (filtered_df["actual_departure"].dt.date >= start_date) &
            (filtered_df["actual_departure"].dt.date <= end_date)
        ]

    st.dataframe(filtered_df, use_container_width=True)

elif page == "Airport Details Viewer":

    st.header("Airport Details Viewer")

    airport_list = sorted(
    airports_df["iata_code"].dropna().unique()
)

    airport_list = sorted(
        airports_df["iata_code"].dropna().unique()
    )

    if len(airport_list) > 0:

        selected_airport = st.selectbox(
            "Select Airport",
            airport_list
        )

        airport_info = airports_df[
            airports_df["iata_code"] == selected_airport
        ]

        airport_flights = flights_df[
            (flights_df["origin_iata"] == selected_airport) |
            (flights_df["destination_iata"] == selected_airport)
        ]

        st.subheader("Airport Information")
        st.dataframe(airport_info, use_container_width=True)

        st.subheader("Linked Flights")
        st.dataframe(airport_flights, use_container_width=True)

    else:

        st.warning("No airport data available.")

elif page == "Delay Analysis":

    st.header("Delay Analysis by Airport")

    delay_stats = airports_df.copy()

    delay_stats["avg_delay_min"] = delay_stats["avg_delay_min"].fillna(0)

    delay_stats = delay_stats.groupby("iata_code").agg(
        avg_delay=("avg_delay_min", "mean"),
        delay_percent=("avg_delay_min", lambda x: (x > 0).mean() * 100)
    ).reset_index()

    delay_stats["avg_delay"] = delay_stats["avg_delay"].abs()

    col1, col2 = st.columns(2)

    fig1 = px.bar(
        delay_stats,
        x="iata_code",
        y="avg_delay",
        title="Average Delay"
    )

    fig2 = px.bar(
        delay_stats,
        x="iata_code",
        y="delay_percent",
        title="Delay Percentage"
    )

    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)

elif page == "Route Leaderboards":

    st.header("Route Leaderboards")

    st.subheader("Busiest Routes")

    route_df = flights_df.dropna(
        subset=["origin_iata", "destination_iata"]
    )

    busiest_routes = (
        route_df.groupby(
            ["origin_iata", "destination_iata"]
        )
        .size()
        .reset_index(name="Flight_Count")
        .sort_values("Flight_Count", ascending=False)
        .head(10)
    )

    st.dataframe(busiest_routes, use_container_width=True)

    st.subheader("Most Delayed Airports")

    delayed_airports = (
        airports_df.groupby("iata_code")["avg_delay_min"]
        .mean()
        .reset_index()
        .sort_values("avg_delay_min", ascending=False)
        .head(10)
    )

    st.dataframe(delayed_airports, use_container_width=True)
