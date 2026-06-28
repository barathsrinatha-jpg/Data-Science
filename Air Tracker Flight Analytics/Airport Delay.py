import requests
import mysql.connector
import pandas as pd
import time
import math
from requests.exceptions import ReadTimeout, RequestException

# ==================================================
# DATABASE CONNECTION
# ==================================================
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Barium@29893",
    database="flight_analytics"
)

connection.autocommit = True
cursor = connection.cursor()

cursor.execute("SELECT DATABASE();")
print("Connected Database:", cursor.fetchone()[0])

# ==================================================
# API CONFIGURATION
# ==================================================
API_HOST = "aerodatabox.p.rapidapi.com"
API_KEY = "b15c300a6bmsh5b86ed4f7051c47p1b9521jsn506aa8bcd035"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

# ==================================================
# AIRPORT LIST (IATA)
# ==================================================
iata_codes = [
    "JEG",   # BGAA
    "YXS",   # CYXS
    "LCY",   # EGLC
    "LHR",   # EGLL
    "NBE",   # DTNH
    "ANR",   # EBAW
    "CPT",   # FACT
    "ACE",   # GCRR
    "AFW",   # KAFW
    "ATS",   # KATS
    "LYH",   # KLYH
    "LCA",   # LCLK
    "CTM",   # MMBT
    "JED",   # OEJN
    "JNU"    # PAJN
]

# ==================================================
# DATAFRAME COLUMNS
# ==================================================
columns = [
    "airport_iata",
    "delay_date",
    "total_flights",
    "delayed_flights",
    "avg_delay_min",
    "median_delay_min",
    "canceled_flights"
]

rows = []

successful = []
failed = []

# ==================================================
# FETCH DELAY DATA
# ==================================================
for iata in iata_codes:

    print(f"Fetching delay data for {iata}...")

    url = f"https://{API_HOST}/airports/iata/{iata}/delays"

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        dep = data.get("departuresDelayInformation", {})

        rows.append((
            iata,
            data.get("from", {}).get("utc"),
            dep.get("numTotal"),
            dep.get("numQualifiedTotal"),
            None,
            dep.get("medianDelay"),
            dep.get("numCancelled")
        ))

        successful.append(iata)

    except ReadTimeout:

        print(f"Timeout : {iata}")
        failed.append(iata)

    except RequestException as e:

        print(f"Failed : {iata}")
        print(e)

        failed.append(iata)

    time.sleep(1.5)

# ==================================================
# CREATE DATAFRAME
# ==================================================
df = pd.DataFrame(rows, columns=columns)

df["delay_date"] = (
    pd.to_datetime(
        df["delay_date"],
        utc=True,
        errors="coerce"
    ).dt.date
)

df["median_delay_min"] = (
    pd.to_timedelta(
        df["median_delay_min"],
        errors="coerce"
    )
    .dt.total_seconds()
    .div(60)
)

df["avg_delay_min"] = df["median_delay_min"]

# Convert NaN → None
df = df.astype(object)
df = df.where(pd.notnull(df), None)

final_rows = list(
    df.itertuples(index=False, name=None)
)

final_rows = [
    tuple(
        None if (
            isinstance(x, float) and math.isnan(x)
        ) else x
        for x in row
    )
    for row in final_rows
]

print(f"\nRows to insert : {len(final_rows)}")

# ==================================================
# INSERT QUERY
# ==================================================
insert_sql = """
INSERT INTO airport_delays
(
    airport_iata,
    delay_date,
    total_flights,
    delayed_flights,
    avg_delay_min,
    median_delay_min,
    canceled_flights
)
VALUES
(%s,%s,%s,%s,%s,%s,%s)

ON DUPLICATE KEY UPDATE

total_flights=VALUES(total_flights),
delayed_flights=VALUES(delayed_flights),
avg_delay_min=VALUES(avg_delay_min),
median_delay_min=VALUES(median_delay_min),
canceled_flights=VALUES(canceled_flights);
"""

cursor.executemany(
    insert_sql,
    final_rows
)

connection.commit()

# ==================================================
# VERIFY DATA
# ==================================================
cursor.execute(
    "SELECT COUNT(*) FROM airport_delays"
)

count = cursor.fetchone()[0]

print("\nRows present in airport_delays table :", count)

# ==================================================
# SUMMARY
# ==================================================
print("\n==============================")
print("SUMMARY")
print("==============================")

print(f"Total Airports : {len(iata_codes)}")
print(f"Successful     : {len(successful)}")
print(f"Failed         : {len(failed)}")

if failed:

    print("\nFailed Airports:")

    for airport in failed:
        print(airport)

# ==================================================
# CLOSE CONNECTION
# ==================================================
cursor.close()
connection.close()

print("\nAirport Delay ETL Completed Successfully.")