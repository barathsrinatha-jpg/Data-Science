"""
=========================================
Module Name : feature_engineering.py

Purpose:
Feature Engineering

Project:
Medical Appointment No Show Prediction
=========================================
"""

import pandas as pd

from config import CLEAN_DATA
from config import PROCESSED_DATA


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    filepath = CLEAN_DATA / "medical_appointments_clean.csv"

    df = pd.read_csv(filepath)

    return df


# ============================================================
# AGE GROUPS
# ============================================================

def create_age_groups(df):

    print("\nCreating Age Groups...")

    bins = [0, 12, 18, 35, 50, 65, 120]

    labels = [
        "Child",
        "Teen",
        "Young Adult",
        "Adult",
        "Senior Adult",
        "Elderly"
    ]

    df["age_group"] = pd.cut(
        df["age"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    return df


# ============================================================
# TARGET ENCODING
# ============================================================

def encode_target(df):

    print("\nEncoding Target Variable...")

    df["no_show_target"] = df["no_show"].map({

        "no": 0,

        "yes": 1

    })

    return df


# ============================================================
# APPOINTMENT TIME CATEGORY
# ============================================================

def appointment_period(df):

    print("\nCreating Appointment Period...")

    def categorize(hour):

        if hour < 10:

            return "Morning"

        elif hour < 14:

            return "Afternoon"

        else:

            return "Evening"

    df["appointment_period"] = df["appointment_time"].apply(categorize)

    return df


# ============================================================
# WEATHER RISK SCORE
# ============================================================

def weather_score(df):

    print("\nCreating Weather Risk Score...")

    score = (

        df["rainy_day_before"]

        + df["storm_day_before"]

    )

    df["weather_risk_score"] = score

    return df


# ============================================================
# CHRONIC DISEASE SCORE
# ============================================================

def health_score(df):

    print("\nCreating Health Score...")

    score = (

        df["hipertension"]

        + df["diabetes"]

        + df["alcoholism"]

        + df["handcap"]

    )

    df["health_score"] = score

    return df


# ============================================================
# COMPANION FLAG
# ============================================================

def companion_flag(df):

    print("\nCreating Companion Flag...")

    df["companion_required"] = df["patient_needs_companion"]

    return df


# ============================================================
# APPOINTMENT DATE
# ============================================================

def create_date_features(df):

    print("\nCreating Date Features...")

    df["appointment_date_continuous"] = pd.to_datetime(
        df["appointment_date_continuous"]
    )

    df["year"] = df["appointment_date_continuous"].dt.year

    df["month"] = df["appointment_date_continuous"].dt.month

    df["day"] = df["appointment_date_continuous"].dt.day

    df["day_of_week"] = df["appointment_date_continuous"].dt.day_name()

    df["week_number"] = df["appointment_date_continuous"].dt.isocalendar().week

    return df


# ============================================================
# SAVE DATASET
# ============================================================

def save_dataset(df):

    filepath = PROCESSED_DATA / "medical_appointments_featured.csv"

    df.to_csv(filepath, index=False)

    print(f"\nFeature Engineered Dataset Saved To\n{filepath}")


# ============================================================
# SUMMARY
# ============================================================

def feature_summary(df):

    print("\n" + "="*60)

    print("FEATURE ENGINEERING SUMMARY")

    print("="*60)

    print(f"Rows : {df.shape[0]}")

    print(f"Columns : {df.shape[1]}")

    print("\nNew Features Created")

    new_columns = [

        "age_group",

        "no_show_target",

        "appointment_period",

        "weather_risk_score",

        "health_score",

        "companion_required",

        "year",

        "month",

        "day",

        "day_of_week",

        "week_number"

    ]

    for column in new_columns:

        print(column)


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_dataset()

    print(f"\nOriginal Shape : {df.shape}")

    df = create_age_groups(df)

    df = encode_target(df)

    df = appointment_period(df)

    df = weather_score(df)

    df = health_score(df)

    df = companion_flag(df)

    df = create_date_features(df)

    save_dataset(df)

    feature_summary(df)

    print(f"\nFinal Shape : {df.shape}")


if __name__ == "__main__":

    main()