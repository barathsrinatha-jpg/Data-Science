"""
=========================================
Module Name : load_data.py

Purpose:
Loads the Medical Appointment dataset
and performs initial data profiling.

Project:
Medical Appointment No-Show Prediction
=========================================
"""

import pandas as pd

from config import RAW_DATA
def load_dataset(filename):

    filepath = RAW_DATA / filename

    df = pd.read_csv(filepath)

    return df
def dataset_information(df):

    print("\n" + "="*70)
    print("DATASET INFORMATION")
    print("="*70)

    print(f"\nShape : {df.shape}")

    print("\nColumns")

    for column in df.columns:
        print(column)
def check_datatypes(df):

    print("\n" + "="*70)
    print("DATA TYPES")
    print("="*70)

    print(df.dtypes)
def missing_values(df):

    print("\n" + "="*70)
    print("MISSING VALUES")
    print("="*70)

    missing = df.isnull().sum()

    missing_percent = (missing / len(df)) * 100

    report = pd.DataFrame({

        "Missing Values": missing,

        "Percentage": missing_percent.round(2)

    })

    print(report)
def duplicate_records(df):

    print("\n" + "="*70)
    print("DUPLICATE RECORDS")
    print("="*70)

    duplicates = df.duplicated().sum()

    print(f"Duplicate Rows : {duplicates}")
def preview_data(df):

    print("\n" + "="*70)
    print("FIRST FIVE ROWS")
    print("="*70)

    print(df.head())
def last_rows(df):

    print("\n" + "="*70)
    print("LAST FIVE ROWS")
    print("="*70)

    print(df.tail())
def statistical_summary(df):

    print("\n" + "="*70)
    print("STATISTICAL SUMMARY")
    print("="*70)

    print(df.describe(include="all"))
def unique_values(df):

    print("\n" + "="*70)
    print("UNIQUE VALUES")
    print("="*70)

    for column in df.columns:

        print(f"\n{column}")

        print(df[column].nunique())
def main():

    df = load_dataset("Medical_appointment_data.csv")

    print("\nCOLUMN NAMES")
    print(df.columns.tolist())

    print("\nDATA TYPES")
    print(df.dtypes)

    dataset_information(df)

    preview_data(df)

    last_rows(df)

    check_datatypes(df)

    missing_values(df)

    duplicate_records(df)

    unique_values(df)

    statistical_summary(df)


if __name__ == "__main__":
    main()