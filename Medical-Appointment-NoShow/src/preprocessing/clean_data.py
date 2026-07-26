"""
=========================================
Module Name : clean_data.py

Purpose:
Clean Medical Appointment Dataset

Project:
Medical Appointment No Show Prediction
=========================================
"""

import pandas as pd

from config import RAW_DATA
from config import CLEAN_DATA
def load_dataset(filename):

    filepath = RAW_DATA / filename

    df = pd.read_csv(filepath)

    return df
cleaning_report = {}
def standardize_columns(df):

    print("\nStandardizing column names...")

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df

def remove_duplicates(df):

    print("\nRemoving duplicate rows...")

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    cleaning_report["Duplicate Rows Removed"] = before - after

    print(f"Removed {before-after} duplicate rows")

    return df
def missing_summary(df):

    print("\nMissing Values")

    missing = df.isnull().sum()

    print(missing)

    return missing

def clean_age(df):

    print("\nCleaning Age...")

    print(df["age"].dtype)

    df["age"] = pd.to_numeric(df["age"], errors="coerce")

    print(df["age"].dtype)

    median_age = df["age"].median()

    df["age"] = df["age"].fillna(median_age)

    return df   

def clean_specialty(df):

    print("\nCleaning Specialty...")

    mode = df["specialty"].mode()[0]

    df["specialty"] = df["specialty"].fillna(mode)

    return df
def clean_disability(df):

    print("\nCleaning Disability...")

    mode = df["disability"].mode()[0]

    df["disability"] = df["disability"].fillna(mode)

    return df
def clean_place(df):

    print("\nCleaning Place...")

    mode = df["place"].mode()[0]

    df["place"] = df["place"].fillna(mode)

    return df
def clean_weather(df):

    print("\nCleaning Weather Columns...")

    weather_columns = [

        "average_temp_day",

        "average_rain_day",

        "max_temp_day",

        "max_rain_day"

    ]

    for column in weather_columns:

        median = df[column].median()

        df[column] = df[column].fillna(median)

    return df
def validate_age(df):

    print("\nValidating Age...")

    before = len(df)

    df = df[(df["age"] >= 0) & (df["age"] <= 110)]

    after = len(df)

    cleaning_report["Invalid Age Records"] = before - after

    print(f"Removed {before-after} invalid ages")

    return df

def clean_text(df):

    print("\nCleaning Text Columns...")

    object_columns = df.select_dtypes(include=["object", "string"]).columns

    for column in object_columns:

        df[column] = df[column].str.strip()

    return df
def convert_binary_columns(df):

    print("\nConverting Binary Columns...")

    binary_columns = [

        "hipertension",

        "diabetes",

        "alcoholism",

        "handcap",

        "scholarship",

        "sms_received"

    ]

    for column in binary_columns:

        if column in df.columns:

            df[column] = df[column].astype(int)

    return df
def final_validation(df):

    print("\nRemaining Missing Values")

    print(df.isnull().sum())

def save_dataset(df):

    output = CLEAN_DATA / "medical_appointments_clean.csv"

    df.to_csv(output, index=False)

    print(f"\nDataset saved to\n{output}")
def print_report():

    print("\n" + "="*60)

    print("DATA CLEANING REPORT")

    print("="*60)

    for key, value in cleaning_report.items():

        print(f"{key} : {value}")

def main():

    df = load_dataset("Medical_appointment_data.csv")

    print(f"Original Shape : {df.shape}")

    missing_summary(df)

    df = standardize_columns(df)

    df = remove_duplicates(df)

    df = clean_age(df)

    df = clean_specialty(df)

    df = clean_disability(df)

    df = clean_place(df)

    df = clean_weather(df)

    df = validate_age(df)

    df = clean_text(df)

    df = convert_binary_columns(df)

    final_validation(df)

    save_dataset(df)

    print_report()

    print(f"\nFinal Shape : {df.shape}")


if __name__ == "__main__":

    main()