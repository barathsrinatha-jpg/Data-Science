import requests
import mysql.connector
import pandas as pd
import time

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

# Verify Database
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
# GET AIRCRAFT DATA FROM API
# ==================================================
def get_aircraft_data(registration):

    url = f"https://{API_HOST}/aircrafts/reg/{registration}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# ==================================================
# READ AIRCRAFT REGISTRATIONS FROM FLIGHTS TABLE
# ==================================================
query = """
SELECT DISTINCT aircraft_registration
FROM flights
WHERE aircraft_registration IS NOT NULL
AND aircraft_registration NOT IN
(
    SELECT registration
    FROM aircraft
);
"""

df = pd.read_sql(query, connection)

aircraft_list = df["aircraft_registration"].tolist()

print("\nAircraft registrations found:", len(aircraft_list))


# ==================================================
# STORE AIRCRAFT DATA
# ==================================================
def store_aircraft_data(data):

    sql = """
    INSERT INTO aircraft
    (
        registration,
        model,
        manufacturer,
        icao_type_code,
        owner
    )
    VALUES
    (
        %s,%s,%s,%s,%s
    )

    ON DUPLICATE KEY UPDATE
        model = VALUES(model),
        manufacturer = VALUES(manufacturer),
        icao_type_code = VALUES(icao_type_code),
        owner = VALUES(owner);
    """

    values = (
        data.get("reg"),
        data.get("typeName"),
        data.get("airlineName"),
        data.get("icaoCode"),
        data.get("productionLine")
    )

    cursor.execute(sql, values)


# ==================================================
# FETCH & STORE
# ==================================================
success = []
failed = []

for registration in aircraft_list:

    try:

        aircraft = get_aircraft_data(registration)

        store_aircraft_data(aircraft)

        print(f"✓ Saved : {registration}")

        success.append(registration)

        time.sleep(1)

    except Exception as e:

        print(f"✗ Failed : {registration}")
        print(f"Reason   : {e}")

        failed.append(registration)


# ==================================================
# SAVE CHANGES
# ==================================================
connection.commit()


# ==================================================
# VERIFY DATA
# ==================================================
print("\n==============================")
print("VERIFYING DATA IN DATABASE")
print("==============================")

cursor.execute("""
SELECT
    aircraft_id,
    registration,
    model,
    manufacturer,
    icao_type_code,
    owner
FROM aircraft
ORDER BY aircraft_id;
""")

rows = cursor.fetchall()

print(f"\nRows present in aircraft table : {len(rows)}\n")

for row in rows:
    print(row)


# ==================================================
# SUMMARY
# ==================================================
print("\n==============================")
print("SUMMARY")
print("==============================")

print(f"Aircraft Found : {len(aircraft_list)}")
print(f"Successful     : {len(success)}")
print(f"Failed         : {len(failed)}")

if failed:
    print("\nFailed Registrations:")
    for reg in failed:
        print(reg)


# ==================================================
# CLOSE CONNECTION
# ==================================================
cursor.close()
connection.close()