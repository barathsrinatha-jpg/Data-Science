import mysql.connector
import pandas as pd

# ==========================
# CONNECT TO MYSQL SERVER
# ==========================
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Barium@29893"
)

cursor = connection.cursor()

# ==========================
# CREATE DATABASE
# ==========================
cursor.execute("CREATE DATABASE IF NOT EXISTS flight_analytics")
print("Database 'flight_analytics' created successfully (or already exists).")

# ==========================
# USE DATABASE
# ==========================
cursor.execute("USE flight_analytics")

# ==========================
# CREATE AIRPORT TABLE
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS airport (
    airport_id INT AUTO_INCREMENT PRIMARY KEY,
    icao_code VARCHAR(10) UNIQUE,
    iata_code VARCHAR(10) UNIQUE,
    name VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255),
    continent VARCHAR(50),
    latitude DOUBLE,
    longitude DOUBLE,
    timezone VARCHAR(50)
);
""")

print("Airport table created successfully.")

# ==========================
# CREATE AIRCRAFT TABLE
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS aircraft (
    aircraft_id INT AUTO_INCREMENT PRIMARY KEY,
    registration VARCHAR(255) UNIQUE,
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    icao_type_code VARCHAR(255),
    owner VARCHAR(255)
);
""")

print("Aircraft table created successfully.")

# ==========================
# CREATE FLIGHTS TABLE
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS flights (
    flight_id VARCHAR(255) PRIMARY KEY,
    flight_number VARCHAR(255),
    aircraft_registration VARCHAR(255),
    origin_iata VARCHAR(255),
    destination_iata VARCHAR(255),
    scheduled_departure VARCHAR(255),
    actual_departure VARCHAR(255),
    scheduled_arrival VARCHAR(255),
    actual_arrival VARCHAR(255),
    status VARCHAR(255),
    airline_code VARCHAR(255),
    aircraft_model VARCHAR(255)
);
""")

print("Flights table created successfully.")

# ==========================
# CREATE AIRPORT DELAYS TABLE
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS airport_delays (
    delay_id INT AUTO_INCREMENT PRIMARY KEY,
    airport_iata VARCHAR(255),
    delay_date VARCHAR(255),
    total_flights INT,
    delayed_flights INT,
    avg_delay_min INT,
    median_delay_min INT,
    canceled_flights INT
);
""")

print("Airport Delays table created successfully.")

# ==========================
# SAVE CHANGES
# ==========================
connection.commit()

# ==========================
# VERIFY FLIGHTS TABLE
# ==========================
df = pd.read_sql_query("SELECT * FROM flights;", connection)

print("\nFlights Table Columns:")
print(df.columns.tolist())

# ==========================
# CLOSE CONNECTION
# ==========================
cursor.close()
connection.close()

print("\nDatabase setup completed successfully.")