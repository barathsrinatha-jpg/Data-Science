import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Barium@29893",
    database="flight_analytics"
)
query1 = """
SELECT
    aircraft_model,
    COUNT(*) AS number_of_flights
FROM (
    SELECT DISTINCT aircraft_model, flight_number
    FROM flights
) a
GROUP BY aircraft_model;
"""

df1 = pd.read_sql(query1, conn)

print("\n============================================================")
print("Question 1: Total Number of Flights for Each Aircraft Model")
print("============================================================")
print(df1)

df1.to_csv("Question1_Total_Number_of_Flights_for_Each_Aircraft_Model.csv", index=False)
query2 = """
SELECT
    COUNT(*) AS number_of_flights,
    aircraft_registration,
    aircraft_model
FROM (
    SELECT DISTINCT aircraft_model,
                    flight_number,
                    aircraft_registration
    FROM flights
) a
WHERE aircraft_registration IS NOT NULL
GROUP BY aircraft_registration,
         aircraft_model
HAVING COUNT(*) > 5;
"""

df2 = pd.read_sql(query2, conn)

print("\n============================================================")
print("Question 2: Aircraft Assigned to More Than 5 Flights")
print("============================================================")
print(df2)

df2.to_csv("Question2_Aircraft_Assigned_to_More_Than_5_Flights.csv", index=False)
query3 = """
SELECT
    b.name AS airport_name,
    COUNT(*) AS number_of_outbound_flights
FROM flights a
JOIN airport b
ON a.origin_iata = b.iata_code
WHERE a.status = 'Departed'
GROUP BY b.name
HAVING COUNT(a.flight_id) > 5;
"""

df3 = pd.read_sql(query3, conn)

print("\n============================================================")
print("Question 3: Airports with More Than 5 Outbound Flights")
print("============================================================")
print(df3)

df3.to_csv("Question3_Airports_with_More_Than_5_Outbound_Flights.csv", index=False)
query4 = """
SELECT
    destination_iata,
    a.name AS airport_name,
    a.city,
    COUNT(*) AS arrival_count
FROM flights f
JOIN airport a
ON f.destination_iata = a.iata_code
GROUP BY
    destination_iata,
    a.name,
    a.city
ORDER BY arrival_count DESC
LIMIT 3;
"""

df4 = pd.read_sql(query4, conn)

print("\n============================================================")
print("Question 4: Top 3 Destination Airports by Number of Arriving Flights")
print("============================================================")
print(df4)

df4.to_csv("Question4_Top_3_Destination_Airports_by_Arriving_Flights.csv", index=False)
query5 = """
SELECT
    f.flight_number,
    o.name AS origin,
    d.name AS destination,
    CASE
        WHEN o.country = d.country THEN 'Domestic'
        ELSE 'International'
    END AS flight_type
FROM flights f
LEFT JOIN airport o
ON f.origin_iata = o.iata_code
LEFT JOIN airport d
ON f.destination_iata = d.iata_code;
"""

df5 = pd.read_sql(query5, conn)

print("\n============================================================")
print("Question 5: Domestic and International Flights")
print("============================================================")
print(df5)

df5.to_csv("Question5_Domestic_and_International_Flights.csv", index=False)
query6 = """
SELECT
    flight_number,
    aircraft_model AS aircraft,
    origin_iata,
    actual_arrival
FROM flights
WHERE destination_iata = 'DEL'
ORDER BY actual_arrival DESC
LIMIT 5;
"""

df6 = pd.read_sql(query6, conn)

print("\n============================================================")
print("Question 6: Five Most Recent Arrivals at DEL Airport")
print("============================================================")
print(df6)

df6.to_csv("Question6_Five_Most_Recent_Arrivals_at_DEL.csv", index=False)
query7 = """
SELECT
    a.*
FROM airport a
LEFT JOIN flights f
ON a.iata_code = f.destination_iata
WHERE f.destination_iata IS NULL;
"""

df7 = pd.read_sql(query7, conn)

print("\n============================================================")
print("Question 7: Airports with No Arriving Flights")
print("============================================================")
print(df7)

df7.to_csv("Question7_Airports_With_No_Arriving_Flights.csv", index=False)
query8 = """
SELECT
    airline_code,
    status,
    COUNT(*) AS number_of_flights
FROM flights
GROUP BY
    airline_code,
    status;
"""

df8 = pd.read_sql(query8, conn)

print("\n============================================================")
print("Question 8: Number of Flights by Airline and Flight Status")
print("============================================================")
print(df8)

df8.to_csv("Question8_Flights_By_Airline_And_Status.csv", index=False)
query9 = """
SELECT
    f.flight_number,
    f.aircraft_model AS aircraft,
    o.name AS origin_airport,
    d.name AS destination_airport,
    f.actual_departure
FROM flights f
LEFT JOIN airport o
ON f.origin_iata = o.iata_code
LEFT JOIN airport d
ON f.destination_iata = d.iata_code
WHERE f.status = 'Canceled'
ORDER BY f.actual_departure DESC;
"""

df9 = pd.read_sql(query9, conn)

print("\n============================================================")
print("Question 9: Cancelled Flights with Aircraft and Airports")
print("============================================================")
print(df9)

df9.to_csv("Question9_Cancelled_Flights.csv", index=False)
query10 = """
SELECT
    ao.city AS origin_city,
    ad.city AS destination_city,
    COUNT(DISTINCT f.aircraft_model) AS aircraft_model_count
FROM flights f
JOIN airport ao
ON f.origin_iata = ao.iata_code
JOIN airport ad
ON f.destination_iata = ad.iata_code
GROUP BY
    ao.city,
    ad.city
HAVING COUNT(DISTINCT f.aircraft_model) > 2;
"""

df10 = pd.read_sql(query10, conn)

print("\n============================================================")
print("Question 10: City Pairs with More Than Two Aircraft Models")
print("============================================================")
print(df10)

df10.to_csv("Question10_City_Pairs_With_More_Than_Two_Aircraft_Models.csv", index=False)
query11 = """
SELECT
    destination_iata,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN status = 'Delayed' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS delayed_percentage
FROM flights
WHERE destination_iata IS NOT NULL
GROUP BY destination_iata
ORDER BY delayed_percentage DESC;
"""

df11 = pd.read_sql(query11, conn)

print("\n============================================================")
print("Question 11: Percentage of Delayed Flights by Destination Airport")
print("============================================================")
print(df11)

df11.to_csv("Question11_Delayed_Flight_Percentage_By_Destination.csv", index=False)