import requests
import mysql.connector

# ==============================
# DATABASE CONNECTION
# ==============================
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

# ==============================
# API CONFIGURATION
# ==============================
API_HOST = "aerodatabox.p.rapidapi.com"
API_KEY = "b15c300a6bmsh5b86ed4f7051c47p1b9521jsn506aa8bcd035"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

# ==============================
# FETCH AIRPORT DATA
# ==============================
def get_airport_data(icao_code):

    url = f"https://{API_HOST}/airports/icao/{icao_code}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# ==============================
# STORE AIRPORT DATA
# ==============================
def store_airport_data(data):

    sql = """
    INSERT INTO airport
    (
        icao_code,
        iata_code,
        name,
        city,
        country,
        continent,
        latitude,
        longitude,
        timezone
    )
    VALUES
    (
        %s,%s,%s,%s,%s,%s,%s,%s,%s
    )
    ON DUPLICATE KEY UPDATE
        iata_code = VALUES(iata_code),
        name = VALUES(name),
        city = VALUES(city),
        country = VALUES(country),
        continent = VALUES(continent),
        latitude = VALUES(latitude),
        longitude = VALUES(longitude),
        timezone = VALUES(timezone);
    """

    values = (
        data.get("icao"),
        data.get("iata"),
        data.get("fullName"),
        data.get("municipalityName"),
        data.get("country", {}).get("name"),
        data.get("continent", {}).get("name"),
        data.get("location", {}).get("lat"),
        data.get("location", {}).get("lon"),
        data.get("timeZone")
    )

    cursor.execute(sql, values)


# ==============================
# ICAO AIRPORT LIST
# ==============================
airport_codes = [
    "BGAA",
    "CYXS",
    "EGLC",
    "EGLL",
    "DTNH",
    "EBAW",
    "FACT",
    "GCRR",
    "KAFW",
    "KATS",
    "KLYH",
    "LCLK",
    "MMBT",
    "OEJN",
    "PAJN"
]

# ==============================
# FETCH & STORE
# ==============================
success = []
failed = []

for code in airport_codes:

    try:

        airport = get_airport_data(code)

        store_airport_data(airport)

        print(f"✓ Saved : {airport.get('fullName')} ({code})")

        success.append(code)

    except Exception as e:

        print(f"✗ Failed : {code}")
        print(e)

        failed.append(code)

# Commit all inserts
connection.commit()

# ==============================
# VERIFY INSERTION
# ==============================
print("\n==============================")
print("VERIFYING DATA IN DATABASE")
print("==============================")

cursor.execute("""
SELECT
    airport_id,
    icao_code,
    iata_code,
    name,
    city,
    country
FROM airport
ORDER BY airport_id;
""")

rows = cursor.fetchall()

print(f"\nRows present in airport table : {len(rows)}\n")

for row in rows:
    print(row)

# ==============================
# SUMMARY
# ==============================
print("\n==============================")
print("SUMMARY")
print("==============================")

print(f"Total Airports : {len(airport_codes)}")
print(f"Successful     : {len(success)}")
print(f"Failed         : {len(failed)}")

if failed:
    print("\nFailed Airports:")
    for code in failed:
        print(code)

# ==============================
# CLOSE CONNECTION
# ==============================
cursor.close()
connection.close()