"""
=========================================
Module Name : eda.py

Purpose:
Exploratory Data Analysis

Project:
Medical Appointment No Show Prediction
=========================================
"""

import matplotlib.pyplot as plt
import pandas as pd

from config import CLEAN_DATA
from config import REPORTS
def load_dataset():

    filepath = CLEAN_DATA / "medical_appointments_clean.csv"

    df = pd.read_csv(filepath)

    return df
def create_output_folder():

    output = REPORTS / "eda"

    output.mkdir(parents=True, exist_ok=True)

    return output
def dataset_overview(df):

    print("\n" + "="*70)
    print("DATASET OVERVIEW")
    print("="*70)

    print(f"Rows : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    print("\nData Types\n")
    print(df.dtypes)
def target_distribution(df, output):

    counts = df["no_show"].value_counts()

    plt.figure(figsize=(6,5))

    counts.plot(kind="bar")

    plt.title("No Show Distribution")

    plt.xlabel("No Show")

    plt.ylabel("Count")

    plt.tight_layout()

    plt.savefig(output / "target_distribution.png")

    plt.close()

    print("\nTarget Distribution")

    print(counts)
def age_distribution(df, output):

    plt.figure(figsize=(8,5))

    plt.hist(df["age"], bins=25)

    plt.title("Age Distribution")

    plt.xlabel("Age")

    plt.ylabel("Frequency")

    plt.tight_layout()

    plt.savefig(output / "age_distribution.png")

    plt.close()
def gender_distribution(df, output):

    plt.figure(figsize=(6,5))

    df["gender"].value_counts().plot(kind="bar")

    plt.title("Gender Distribution")

    plt.tight_layout()

    plt.savefig(output / "gender_distribution.png")

    plt.close()
def specialty_distribution(df, output):

    plt.figure(figsize=(10,5))

    df["specialty"].value_counts().plot(kind="bar")

    plt.title("Specialty Distribution")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(output / "specialty_distribution.png")

    plt.close()
def specialty_distribution(df, output):

    plt.figure(figsize=(10,5))

    df["specialty"].value_counts().plot(kind="bar")

    plt.title("Specialty Distribution")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(output / "specialty_distribution.png")

    plt.close()
def appointment_shift(df, output):

    plt.figure(figsize=(6,5))

    df["appointment_shift"].value_counts().plot(
        kind="bar"
    )

    plt.title("Appointment Shift Distribution")

    plt.xlabel("Appointment Shift")

    plt.ylabel("Count")

    plt.tight_layout()

    plt.savefig(output / "appointment_shift.png")

    plt.close()
    
def no_show_gender(df, output):

    table = pd.crosstab(df["gender"], df["no_show"])

    table.plot(kind="bar", figsize=(7,5))

    plt.title("No Show by Gender")

    plt.tight_layout()

    plt.savefig(output / "no_show_gender.png")

    plt.close()
def no_show_specialty(df, output):

    table = pd.crosstab(df["specialty"], df["no_show"])

    table.plot(kind="bar", figsize=(10,5))

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(output / "no_show_specialty.png")

    plt.close()
def sms_analysis(df, output):

    table = pd.crosstab(df["sms_received"], df["no_show"])

    table.plot(kind="bar", figsize=(7,5))

    plt.title("SMS Received vs No Show")

    plt.tight_layout()

    plt.savefig(output / "sms_analysis.png")

    plt.close()
def correlation_heatmap(df, output):

    numeric = df.select_dtypes(include="number")

    correlation = numeric.corr()

    plt.figure(figsize=(12,10))

    plt.imshow(correlation)

    plt.colorbar()

    plt.xticks(range(len(correlation.columns)),
               correlation.columns,
               rotation=90)

    plt.yticks(range(len(correlation.columns)),
               correlation.columns)

    plt.tight_layout()

    plt.savefig(output / "correlation_heatmap.png")

    plt.close()
def appointment_trend(df, output):

    df["appointment_date_continuous"] = pd.to_datetime(
        df["appointment_date_continuous"]
    )

    daily = (
        df.groupby("appointment_date_continuous")
        .size()
    )

    plt.figure(figsize=(12,5))

    daily.plot()

    plt.title("Daily Appointments")

    plt.tight_layout()

    plt.savefig(output / "daily_appointments.png")

    plt.close()
def weather_analysis(df, output):

    plt.figure(figsize=(8,5))

    plt.scatter(
        df["average_temp_day"],
        df["appointment_time"],
        alpha=0.3
    )

    plt.xlabel("Average Temperature")

    plt.ylabel("Appointment Time")

    plt.tight_layout()

    plt.savefig(output / "weather_analysis.png")

    plt.close()
def main():

    df = load_dataset()

    output = create_output_folder()

    dataset_overview(df)

    target_distribution(df, output)

    age_distribution(df, output)

    gender_distribution(df, output)

    specialty_distribution(df, output)

    appointment_shift(df, output)

    no_show_gender(df, output)

    no_show_specialty(df, output)

    sms_analysis(df, output)

    correlation_heatmap(df, output)

    appointment_trend(df, output)

    weather_analysis(df, output)

    print("\nEDA Completed Successfully.")

if __name__ == "__main__":
    main()