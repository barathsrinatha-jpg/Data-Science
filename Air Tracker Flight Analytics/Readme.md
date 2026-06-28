# ✈️ Air Tracker: Flight Analytics

## 📌 Project Overview

Air Tracker: Flight Analytics is a Python-based data analytics project that extracts aviation data from the AeroDataBox API, stores it in a MySQL database, performs SQL-based analysis, and presents interactive dashboards using Streamlit.

The project enables users to explore airports, aircraft, flights, and airport delays while generating useful operational insights through SQL queries and interactive visualizations.

---

# 🎯 Objectives

- Extract aviation data from AeroDataBox API.
- Parse nested JSON responses.
- Store structured data in MySQL.
- Perform SQL analytics on flight operations.
- Develop an interactive Streamlit dashboard.
- Visualize airport performance and flight trends.

---

# 🛠 Technologies Used

- Python 3
- MySQL
- Streamlit
- Pandas
- Plotly Express
- Requests
- MySQL Connector
- AeroDataBox API

---

# 📂 Project Structure

```
Air Tracker Flight Analytics
│
├── Airport Data Extraction.py
├── Aircraft Data Extraction.py
├── Flight Data Extraction.py
├── Airport Delay.py
├── SQL Table.py
├── SQL Queries.py
├── Streamlit.py
├── README.md
```

---

# 🗄 Database Schema

The project uses four tables.

## Airport

Stores airport information.

Fields:

- Airport ID
- ICAO Code
- IATA Code
- Airport Name
- City
- Country
- Continent
- Latitude
- Longitude
- Timezone

---

## Aircraft

Stores aircraft details.

Fields:

- Aircraft ID
- Registration
- Model
- Manufacturer
- ICAO Type Code
- Owner

---

## Flights

Stores flight schedule and operational details.

Fields:

- Flight ID
- Flight Number
- Aircraft Registration
- Origin Airport
- Destination Airport
- Scheduled Departure
- Actual Departure
- Scheduled Arrival
- Actual Arrival
- Flight Status
- Airline Code

---

## Airport Delays

Stores airport delay statistics.

Fields:

- Delay ID
- Airport IATA
- Delay Date
- Total Flights
- Delayed Flights
- Average Delay
- Median Delay
- Cancelled Flights

---

# 📊 SQL Analysis

The project answers the following analytical questions.

1. Total flights for each aircraft model.

2. Aircraft assigned to more than five flights.

3. Airports having more than five outbound flights.

4. Top three destination airports by arrivals.

5. Domestic vs International flights.

6. Five most recent arrivals at DEL airport.

7. Airports with no arriving flights.

8. Flight status count by airline.

9. Cancelled flights with origin and destination airports.

10. City pairs operated by more than two aircraft models.

11. Percentage of delayed arrivals for each destination airport.

---

# 📈 Streamlit Dashboard Features

The Streamlit application contains the following modules.

## 🏠 Homepage Dashboard

Displays

- Total Airports
- Total Flights
- Average Airport Delay
- Flights per Airport Chart

---

## 🔍 Search & Filter Flights

Users can

- Search Flight Number
- Search Airline
- Filter by Status
- Filter by Origin Airport
- Filter by Departure Date

---

## 🏢 Airport Details Viewer

Displays

- Airport Information
- Airport Location
- Timezone
- Linked Flights

---

## ⏱ Delay Analysis

Visualizes

- Average Delay by Airport
- Delay Percentage by Airport

---

## 🏆 Route Leaderboards

Displays

- Top 10 Busiest Routes
- Most Delayed Airports

---

# 📊 Libraries Used

```python
streamlit
pandas
mysql-connector-python
plotly
requests
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Air-Tracker-Flight-Analytics.git
```

Go to project folder

```bash
cd Air-Tracker-Flight-Analytics
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🗄 Database Setup

1. Install MySQL Server.

2. Create database.

```sql
CREATE DATABASE flight_analytics;
```

3. Run SQL Table.py to create all tables.

4. Run the extraction scripts to populate the database.

---

# ▶ Running the Project

Run the Streamlit dashboard.

```bash
streamlit run Streamlit.py
```

The application opens at

```
http://localhost:8501
```

---

# 📌 Skills Demonstrated

- API Integration
- JSON Parsing
- Data Cleaning
- Relational Database Design
- SQL Query Writing
- Data Analysis
- Interactive Dashboard Development
- Python Programming
- Streamlit Development

---

# 🚀 Future Enhancements

- Live Flight Tracking
- Real-time API Updates
- Interactive World Map
- Airline Performance Dashboard
- Flight Delay Prediction using Machine Learning
- User Authentication
- Download Reports as PDF or Excel

---

# 👨‍💻 Author

**Barath Srinath A**

Project completed as part of the **GUVI Data Science Project**.

---

# 📚 References

- AeroDataBox API
- RapidAPI
- Streamlit Documentation
- Pandas Documentation
- Plotly Documentation
- MySQL Documentation

---

# 📄 License

This project is developed for educational purposes as part of the GUVI Data Science Program.