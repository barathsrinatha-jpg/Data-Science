"""
=========================================
Module Name : train_forecasting.py

Purpose:
Appointment Demand Forecasting

Project:
Medical Appointment No Show Prediction
=========================================
"""

import joblib
import pandas as pd

from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor

from config import PROCESSED_DATA


# =====================================================
# LOAD DATA
# =====================================================

def load_dataset():

    filepath = PROCESSED_DATA / "medical_appointments_featured.csv"

    df = pd.read_csv(filepath)

    return df


# =====================================================
# DAILY APPOINTMENTS
# =====================================================

def prepare_daily_data(df):

    df["appointment_date_continuous"] = pd.to_datetime(
        df["appointment_date_continuous"]
    )

    daily = (

        df.groupby("appointment_date_continuous")

        .size()

        .reset_index(name="appointments")

        .sort_values("appointment_date_continuous")

    )

    return daily


# =====================================================
# CREATE LAG FEATURES
# =====================================================

def create_features(df):

    df = df.copy()

    df["day_of_week"] = df["appointment_date_continuous"].dt.dayofweek

    df["month"] = df["appointment_date_continuous"].dt.month

    df["day"] = df["appointment_date_continuous"].dt.day

    df["lag_1"] = df["appointments"].shift(1)

    df["lag_7"] = df["appointments"].shift(7)

    df["rolling_mean_7"] = (

        df["appointments"]

        .rolling(7)

        .mean()

    )

    df = df.dropna()

    return df


# =====================================================
# TRAIN TEST SPLIT
# =====================================================

def split_data(df):

    features = [

        "day_of_week",

        "month",

        "day",

        "lag_1",

        "lag_7",

        "rolling_mean_7"

    ]

    X = df[features]

    y = df["appointments"]

    split = int(len(df) * 0.80)

    X_train = X.iloc[:split]

    X_test = X.iloc[split:]

    y_train = y.iloc[:split]

    y_test = y.iloc[split:]

    return X_train, X_test, y_train, y_test


# =====================================================
# MODELS
# =====================================================

def get_models():

    return {

        "Linear Regression":

            LinearRegression(),

        "Random Forest":

            RandomForestRegressor(

                n_estimators=200,

                random_state=42

            ),

        "XGBoost":

            XGBRegressor(

                random_state=42,

                objective="reg:squarederror"

            )

    }


# =====================================================
# TRAIN
# =====================================================

def train_models(X_train, X_test, y_train, y_test):

    results = []

    best_model = None

    best_name = ""

    best_rmse = float("inf")

    for name, model in get_models().items():

        print(f"\nTraining {name}...")

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        mae = mean_absolute_error(

            y_test,

            predictions

        )

        mse = mean_squared_error(

            y_test,

            predictions,

        )
        rmse = mse ** 0.5
        r2 = r2_score(

            y_test,

            predictions

        )

        results.append({

            "Model": name,

            "MAE": round(mae, 2),

            "RMSE": round(rmse, 2),

            "R2": round(r2, 4)

        })

        if rmse < best_rmse:

            best_rmse = rmse

            best_model = model

            best_name = name

    return pd.DataFrame(results), best_model, best_name


# =====================================================
# SAVE MODEL
# =====================================================

def save_model(model):

    folder = Path("models")

    folder.mkdir(exist_ok=True)

    filepath = folder / "best_forecasting_model.pkl"

    joblib.dump(model, filepath)

    print(f"\nForecasting model saved to {filepath}")


# =====================================================
# MAIN
# =====================================================

def main():

    print("=" * 60)

    print("APPOINTMENT DEMAND FORECASTING")

    print("=" * 60)

    df = load_dataset()

    daily = prepare_daily_data(df)

    daily = create_features(daily)

    X_train, X_test, y_train, y_test = split_data(daily)

    results, best_model, best_name = train_models(

        X_train,

        X_test,

        y_train,

        y_test

    )

    print("\n")

    print(results)

    print(f"\nBest Model : {best_name}")

    save_model(best_model)


if __name__ == "__main__":

    main()