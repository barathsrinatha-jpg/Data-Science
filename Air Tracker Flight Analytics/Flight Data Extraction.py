import requests
import mysql.connector
import pandas as pd

# ==================================================
# DATABASE CONNECTION
# ==================================================
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Barium@29893",
    database="flight_analytics"
)

cursor = connection.cursor()

cursor.execute("SELECT DATABASE();")
print("Connected Database:", cursor.fetchone()[0])

# ==================================================
# API CONFIGURATION
# ==================================================
API_HOST = "aerodatabox.p.rapidapi.com"
API_KEY = "232e995e0cmshd34dc590f07dfedp1cf8f5jsne2fe2f5f3d98"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

# ==================================================
# COLUMNS
# ==================================================
columns = [
    "flight_id",
    "flight_number",
    "aircraft_registration",
    "origin_iata",
    "destination_iata",
    "scheduled_departure",
    "actual_departure",
    "scheduled_arrival",
    "actual_arrival",
    "status",
    "airline_code",
    "aircraft_model"
]

departure_data = {c: [] for c in columns}
arrival_data = {c: [] for c in columns}

# ==================================================
# AIRPORTS (IATA Codes)
# ==================================================
AIRPORT_CODES = [
    "JEG",  # BGAA
    "YXS",  # CYXS
    "LCY",  # EGLC
    "LHR",  # EGLL
    "NBE",  # DTNH
    "ANR",  # EBAW
    "CPT",  # FACT
    "ACE",  # GCRR
    "AFW",  # KAFW
    "ATS",  # KATS
    "LYH",  # KLYH
    "LCA",  # LCLK
    "CTM",  # MMBT
    "JED",  # OEJN
    "JNU"   # PAJN
]

successful = []
failed = []

# ==================================================
# FETCH FLIGHT DATA
# ==================================================
for airport in AIRPORT_CODES:

    try:

        print(f"Fetching flights for {airport}...")

        url = f"https://{API_HOST}/flights/airports/iata/{airport}"

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        successful.append(airport)

    except Exception as e:

        print(f"Failed : {airport}")
        print(e)

        failed.append(airport)

        continue

    # ----------------- DEPARTURES -----------------

    for i in data.get("departures", []):

        departure_data["flight_id"].append(
            f"{i.get('number','NA')}_{i['movement']['scheduledTime'].get('utc','NA')}"
        )

        departure_data["flight_number"].append(i.get("number"))

        departure_data["aircraft_registration"].append(
            i.get("aircraft", {}).get("reg")
        )

        departure_data["origin_iata"].append(
            i["movement"]["airport"].get("iata")
        )

        departure_data["destination_iata"].append(None)

        departure_data["scheduled_departure"].append(
            i["movement"]["scheduledTime"].get("utc")
        )

        departure_data["actual_departure"].append(
            i["movement"].get("revisedTime", {}).get("utc")
        )

        departure_data["scheduled_arrival"].append(None)

        departure_data["actual_arrival"].append(None)

        departure_data["status"].append(i.get("status"))

        departure_data["airline_code"].append(
            i.get("airline", {}).get("iata")
        )

        departure_data["aircraft_model"].append(
            i.get("aircraft", {}).get("model")
        )

    # ----------------- ARRIVALS -----------------

    for i in data.get("arrivals", []):

        arrival_data["flight_id"].append(
            f"{i.get('number','NA')}_{i['movement']['scheduledTime'].get('utc','NA')}"
        )

        arrival_data["flight_number"].append(i.get("number"))

        arrival_data["aircraft_registration"].append(
            i.get("aircraft", {}).get("reg")
        )

        arrival_data["origin_iata"].append(None)

        arrival_data["destination_iata"].append(
            i["movement"]["airport"].get("iata")
        )

        arrival_data["scheduled_departure"].append(None)

        arrival_data["actual_departure"].append(None)

        arrival_data["scheduled_arrival"].append(
            i["movement"]["scheduledTime"].get("utc")
        )

        arrival_data["actual_arrival"].append(
            i["movement"].get("revisedTime", {}).get("utc")
        )

        arrival_data["status"].append(i.get("status"))

        arrival_data["airline_code"].append(
            i.get("airline", {}).get("iata")
        )

        arrival_data["aircraft_model"].append(
            i.get("aircraft", {}).get("model")
        )

# ==================================================
# CREATE DATAFRAME
# ==================================================
df = pd.concat(
    [
        pd.DataFrame(departure_data),
        pd.DataFrame(arrival_data)
    ],
    ignore_index=True
)

df.drop_duplicates(subset=["flight_id"], inplace=True)
df = df.astype(object)
df = df.where(pd.notnull(df), None)

print(f"\nFlights collected : {len(df)}")

# ==================================================
# INSERT INTO MYSQL
# ==================================================
insert_sql = """
INSERT INTO flights
(
flight_id,
flight_number,
aircraft_registration,
origin_iata,
destination_iata,
scheduled_departure,
actual_departure,
scheduled_arrival,
actual_arrival,
status,
airline_code,
aircraft_model
)
VALUES
(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

ON DUPLICATE KEY UPDATE
aircraft_registration=VALUES(aircraft_registration),
origin_iata=VALUES(origin_iata),
destination_iata=VALUES(destination_iata),
actual_departure=VALUES(actual_departure),
actual_arrival=VALUES(actual_arrival),
status=VALUES(status),
airline_code=VALUES(airline_code),
aircraft_model=VALUES(aircraft_model);
"""

cursor.executemany(
    insert_sql,
    list(df[columns].itertuples(index=False, name=None))
)

connection.commit()

# ==================================================
# VERIFY DATA
# ==================================================
cursor.execute("SELECT COUNT(*) FROM flights")

count = cursor.fetchone()[0]

print("\nRows present in flights table :", count)

print("\nSuccessful Airports :", len(successful))
print("Failed Airports     :", len(failed))

if failed:
    print("\nFailed Airport Codes:")
    for airport in failed:
        print(airport)

cursor.close()
connection.close()

print("\nFlight ETL Completed Successfully.")