import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

file_path = r"C:\Users\barat\OneDrive\Documents\GitHub\Data-Science\Marketing_Campaign_Analysis\data\processed\marketing_segmented.csv"

df = pd.read_csv(file_path)

username = "root"
password = "Barium@29893"

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=username,
    password=password,
    host="localhost",
    port=3306,
    database="marketing_campaign_analysis"
)

engine = create_engine(connection_url)

print("Connected Successfully")
df.to_sql(
    name="customers",
    con=engine,
    if_exists="append",
    index=False
)

print("Data Uploaded Successfully")