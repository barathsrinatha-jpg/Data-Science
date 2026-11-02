import os
import re
import textwrap
import time

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

# A flight is "Delayed" if the API says so or it ran more than 15 minutes late.
DELAYED = "(status = 'Delayed' OR delay_minutes > 15)"
CANCELLED = "(status LIKE 'Cancel%')"


def _clean(df):
    """Turn MySQL Decimal values into floats so pandas and Plotly can use them."""
    for col in df.columns:
        if df[col].map(lambda v: type(v).__name__ == "Decimal").any():
            df[col] = pd.to_numeric(df[col].astype(float), errors="coerce")
    return df


def run_live(sql):
    """Run a SELECT straight against MySQL (no caching) and return a DataFrame."""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
    finally:
        conn.close()
    return _clean(df)


@st.cache_data(ttl=300, show_spinner=False)
def run_query(sql):
    """Cached version, used for the page data so filters stay fast."""
    return run_live(sql)


# (number, title, sql, chart) - chart is (x column, [y columns]) or None
QUERIES = [
    (1, "Total number of flights for each aircraft model", """
        SELECT aircraft_model, COUNT(*) AS number_of_flights
        FROM flights
        WHERE aircraft_model IS NOT NULL
        GROUP BY aircraft_model
        ORDER BY number_of_flights DESC
    """, ("aircraft_model", ["number_of_flights"])),
    (2, "Aircraft assigned to more than 5 flights", """
        SELECT f.aircraft_registration AS registration,
               COALESCE(a.model, MAX(f.aircraft_model)) AS model,
               COUNT(*) AS number_of_flights
        FROM flights f
        LEFT JOIN aircraft a ON a.registration = f.aircraft_registration
        WHERE f.aircraft_registration IS NOT NULL
        GROUP BY f.aircraft_registration, a.model
        HAVING COUNT(*) > 5
        ORDER BY number_of_flights DESC
    """, ("registration", ["number_of_flights"])),
    (3, "Airports with more than 5 outbound flights", """
        SELECT a.name AS airport_name, COUNT(*) AS outbound_flights
        FROM airport a
        JOIN flights f ON f.origin_iata = a.iata_code
        GROUP BY a.name
        HAVING COUNT(*) > 5
        ORDER BY outbound_flights DESC
    """, ("airport_name", ["outbound_flights"])),
    (4, "Top 3 destination airports by arriving flights", """
        SELECT a.name AS airport_name, a.city, COUNT(*) AS arriving_flights
        FROM flights f
        JOIN airport a ON a.iata_code = f.destination_iata
        GROUP BY a.name, a.city
        ORDER BY arriving_flights DESC
        LIMIT 3
    """, ("airport_name", ["arriving_flights"])),
    (5, "Domestic or International flights", """
        SELECT flight_number, origin_iata AS origin, destination_iata AS destination,
               CASE WHEN origin_country_code = destination_country_code
                    THEN 'Domestic' ELSE 'International' END AS flight_type
        FROM flights
        WHERE origin_country_code IS NOT NULL AND destination_country_code IS NOT NULL
        ORDER BY flight_number
    """, None),
    (6, "Five most recent arrivals at DEL", """
        SELECT flight_number,
               COALESCE(aircraft_registration, aircraft_model) AS aircraft,
               origin_airport_name AS departure_airport,
               COALESCE(actual_arrival, scheduled_arrival) AS arrival_time
        FROM flights
        WHERE destination_iata = 'DEL' AND scheduled_arrival IS NOT NULL
        ORDER BY arrival_time DESC
        LIMIT 5
    """, None),
    (7, "Airports with no arriving flights", """
        SELECT a.iata_code, a.name, a.city
        FROM airport a
        LEFT JOIN flights f ON f.destination_iata = a.iata_code
        WHERE f.flight_id IS NULL
    """, None),
    (8, "Flights by airline and status (On Time / Delayed / Cancelled)", f"""
        SELECT airline_code,
               SUM(CASE WHEN {CANCELLED} THEN 1 ELSE 0 END)                    AS cancelled_flights,
               SUM(CASE WHEN NOT {CANCELLED} AND {DELAYED} THEN 1 ELSE 0 END)  AS delayed_flights,
               SUM(CASE WHEN NOT {CANCELLED} AND NOT COALESCE({DELAYED}, 0)
                        THEN 1 ELSE 0 END)                                      AS on_time_flights,
               COUNT(*) AS total
        FROM flights
        WHERE airline_code IS NOT NULL
        GROUP BY airline_code
        ORDER BY total DESC
    """, ("airline_code", ["cancelled_flights", "delayed_flights", "on_time_flights"])),
    (9, "Cancelled flights with aircraft and both airports", f"""
        SELECT flight_number,
               COALESCE(aircraft_registration, aircraft_model) AS aircraft,
               origin_airport_name AS origin_airport,
               destination_airport_name AS destination_airport,
               COALESCE(scheduled_departure, scheduled_arrival) AS flight_time
        FROM flights
        WHERE {CANCELLED}
        ORDER BY flight_time DESC
    """, None),
    (10, "Airport pairs served by more than 2 aircraft models", """
        SELECT origin_iata, destination_iata,
               COUNT(DISTINCT aircraft_model) AS aircraft_models
        FROM flights
        WHERE aircraft_model IS NOT NULL
        GROUP BY origin_iata, destination_iata
        HAVING COUNT(DISTINCT aircraft_model) > 2
        ORDER BY aircraft_models DESC
    """, ("route", ["aircraft_models"])),
    (11, "Percentage of delayed arrivals per destination airport", f"""
        SELECT destination_iata, MAX(destination_airport_name) AS airport,
               COUNT(*) AS arrivals,
               ROUND(100 * SUM(CASE WHEN COALESCE({DELAYED}, 0) THEN 1 ELSE 0 END) / COUNT(*), 2)
                   AS delayed_percentage
        FROM flights
        WHERE scheduled_arrival IS NOT NULL AND NOT {CANCELLED}
        GROUP BY destination_iata
        HAVING COUNT(*) >= 5
        ORDER BY delayed_percentage DESC
    """, ("destination_iata", ["delayed_percentage"])),
]

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|replace|rename|"
    r"outfile|dumpfile|load_file|call|set|lock|unlock|handler)\b",
    re.IGNORECASE,
)


def check_read_only(sql):
    """Return an error message if the text is not a single read-only SELECT."""
    text = sql.strip().rstrip(";").strip()
    if not text:
        return "Type a query first."
    if ";" in text:
        return "Only one statement at a time, please."
    if not re.match(r"^(select|with)\b", text, re.IGNORECASE):
        return "Only SELECT queries are allowed."
    if FORBIDDEN.search(text):
        return "This query contains a keyword that is not allowed (read-only mode)."
    return None


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
        "SQL Queries",
    ],
)

if page == "Homepage Dashboard":
    st.header("Summary Statistics")

    f1, f2, f3 = st.columns(3)
    sel_airlines = f1.multiselect("Airline", sorted(flights_df["airline_code"].dropna().unique()))
    sel_status = f2.multiselect("Status", sorted(flights_df["status"].dropna().unique()))
    sel_airports = f3.multiselect("Airport", airports_df["iata_code"].tolist())

    view = flights_df
    if sel_airlines:
        view = view[view["airline_code"].isin(sel_airlines)]
    if sel_status:
        view = view[view["status"].isin(sel_status)]
    if sel_airports:
        view = view[view["origin_iata"].isin(sel_airports) | view["destination_iata"].isin(sel_airports)]

    total_flights = len(view)
    delayed = ((view["status"] == "Delayed") | (view["delay_minutes"] > 15)).sum()
    delays = view["delay_minutes"].dropna().clip(lower=0)
    avg_delay = float(delays.mean()) if len(delays) else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Airports", len(airports_df))
    c2.metric("Total Flights Fetched", f"{total_flights:,}")
    c3.metric("Average Delay (mins)", round(avg_delay, 2))
    c4.metric("Delayed Flights", f"{100 * delayed / max(total_flights, 1):.1f}%")

    st.divider()
    if view.empty:
        st.warning("No flights match these filters.")
    else:
        left, right = st.columns(2)

        traffic = (
            pd.concat([view["origin_iata"], view["destination_iata"]])
            .value_counts()
            .reindex(airports_df["iata_code"])
            .fillna(0)
            .reset_index()
        )
        traffic.columns = ["Airport", "Flights"]
        left.subheader("Flights per Airport")
        left.plotly_chart(px.bar(traffic, x="Airport", y="Flights"), width="stretch")

        status_counts = view["status"].fillna("Unknown").value_counts().reset_index()
        status_counts.columns = ["Status", "Flights"]
        right.subheader("Flights by Status")
        right.plotly_chart(px.pie(status_counts, names="Status", values="Flights"), width="stretch")

elif page == "Search & Filter Flights":
    st.header("Search & Filter Flights")

    col1, col2 = st.columns(2)
    search_flight = col1.text_input("Search Flight Number")
    search_airline = col2.text_input("Search Airline Code")

    col3, col4, col5 = st.columns(3)
    status_filter = col3.selectbox(
        "Filter by Status", ["All"] + sorted(flights_df["status"].dropna().unique().tolist())
    )
    origin_filter = col4.selectbox(
        "Filter by Origin", ["All"] + sorted(flights_df["origin_iata"].dropna().unique().tolist())
    )
    destination_filter = col5.selectbox(
        "Filter by Destination", ["All"] + sorted(flights_df["destination_iata"].dropna().unique().tolist())
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
    if destination_filter != "All":
        result = result[result["destination_iata"] == destination_filter]
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
        f1, f2 = st.columns(2)
        chosen = f1.multiselect("Airports", delay_df["airport_iata"].tolist(),
                                default=delay_df["airport_iata"].tolist())
        min_flights = f2.slider("Minimum flights", 0, int(delay_df["total_flights"].max()), 0)
        shown = delay_df[delay_df["airport_iata"].isin(chosen) & (delay_df["total_flights"] >= min_flights)]

        if shown.empty:
            st.warning("No airports match these filters.")
        else:
            c1, c2 = st.columns(2)
            c1.plotly_chart(
                px.bar(shown, x="airport_iata", y="avg_delay_min", title="Average Delay (minutes)"),
                width="stretch",
            )
            c2.plotly_chart(
                px.bar(shown, x="airport_iata", y="delay_pct", title="Delayed Flights (%)"),
                width="stretch",
            )
            st.plotly_chart(
                px.bar(shown, x="airport_iata", y="canceled_flights", title="Cancelled Flights"),
                width="stretch",
            )
            st.dataframe(shown.sort_values("delay_pct", ascending=False), width="stretch")

elif page == "Route Leaderboards":
    st.header("Route Leaderboards")

    f1, f2 = st.columns(2)
    sel_airlines = f1.multiselect("Airline", sorted(flights_df["airline_code"].dropna().unique()))
    sel_status = f2.multiselect("Status", sorted(flights_df["status"].dropna().unique()))
    route_source = flights_df.dropna(subset=["origin_iata", "destination_iata"])
    if sel_airlines:
        route_source = route_source[route_source["airline_code"].isin(sel_airlines)]
    if sel_status:
        route_source = route_source[route_source["status"].isin(sel_status)]

    st.subheader("Busiest Routes")
    routes = (
        route_source.groupby(["origin_iata", "destination_iata"])
        .size()
        .reset_index(name="Flights")
        .sort_values("Flights", ascending=False)
        .head(10)
    )
    if routes.empty:
        st.warning("No routes match these filters.")
    else:
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

elif page == "SQL Queries":
    st.header("SQL Queries")
    st.caption("Each query runs live against the MySQL database every time it is shown.")

    labels = [f"Q{n}. {title}" for n, title, _, _ in QUERIES]
    choice = st.selectbox("Choose a question", labels)
    number, title, sql, chart = QUERIES[labels.index(choice)]
    sql = textwrap.dedent(sql).strip()

    st.subheader(f"Question {number}: {title}")
    st.code(sql, language="sql")

    started = time.perf_counter()
    try:
        result = run_live(sql)
    except mysql.connector.Error as err:
        st.error(f"Query failed: {err}")
        st.stop()
    elapsed = time.perf_counter() - started

    m1, m2 = st.columns(2)
    m1.metric("Rows returned", f"{len(result):,}")
    m2.metric("Run time", f"{elapsed:.3f} s")

    if result.empty:
        st.info("The query ran successfully and returned no rows.")
    else:
        st.dataframe(result.head(1000), width="stretch")
        if len(result) > 1000:
            st.caption(f"Showing the first 1,000 of {len(result):,} rows (the download has them all).")
        st.download_button(
            "Download result as CSV",
            result.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"question_{number}.csv",
            mime="text/csv",
        )

        if chart:
            x_col, y_cols = chart
            plot = result.head(15).copy()
            if x_col == "route":
                plot["route"] = plot["origin_iata"] + " → " + plot["destination_iata"]
            st.plotly_chart(
                px.bar(plot, x=x_col, y=y_cols, barmode="stack" if len(y_cols) > 1 else "relative",
                       title=f"Question {number} (top {len(plot)})"),
                width="stretch",
            )

    st.divider()
    with st.expander("Run your own SELECT query"):
        custom = st.text_area("SQL", "SELECT * FROM airport", height=120)
        if st.button("Run my query"):
            problem = check_read_only(custom)
            if problem:
                st.error(problem)
            else:
                try:
                    custom_df = run_live(custom.strip().rstrip(";"))
                    st.success(f"{len(custom_df):,} rows returned")
                    st.dataframe(custom_df.head(1000), width="stretch")
                except mysql.connector.Error as err:
                    st.error(f"Query failed: {err}")
