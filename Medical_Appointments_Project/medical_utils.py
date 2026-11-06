"""Shared helpers for the Medical Appointment No-Show & Demand Forecasting project.

The notebook (training) and app.py (deployment) both import this module, so features are
built in exactly the same way when a model is trained and when it is used.
"""
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------------------
# Data constants
# --------------------------------------------------------------------------------------
# The 13 cities served by the clinic. Every other value in the raw `place` column is a
# made-up name (about 26,000 of them) and is grouped as OTHER_NAME.
REAL_CITIES = ["ITAJAÍ", "B. CAMBORIU", "CAMBORIU", "NAVEGANTES", "ITAPEMA", "BOMBINHAS", "PENHA",
               "PORTO BELO", "BALN. PIÇARRAS", "ILHOTA", "LUIZ ALVES", "MONTENEGRO", "BLUMENAU"]
OTHER_PLACE = "OTHER_NAME"
MISSING_PLACE = "MISSING"
SPECIALTY_MAP = {"enf": "nursing", "assist": "social work", "pedagogo": "pedagogy", "sem especialidade": "no specialty"}

# Columns used by the no-show classifier
CLS_CATEGORICAL = ["place", "specialty", "disability", "gender", "appointment_shift", "rain_intensity",
                   "heat_intensity", "age_group", "appointment_period"]
CLS_NUMERIC = ["age", "age_missing", "appointment_time", "under_12_years_old", "over_60_years_old",
               "patient_needs_companion", "average_temp_day", "average_rain_day", "max_temp_day", "max_rain_day",
               "storm_day_before", "weather_missing", "hipertension", "diabetes", "alcoholism", "handcap",
               "scholarship", "sms_received", "weather_risk_score", "health_score", "month", "day_of_week",
               "is_weekend"]

# Daily weather columns used by the demand forecaster
WEATHER_COLS = ["average_temp_day", "average_rain_day", "max_rain_day", "storm_day_before"]


# --------------------------------------------------------------------------------------
# Feature engineering for the no-show classifier (works on a whole table or on one row)
# --------------------------------------------------------------------------------------
def engineer_features(df):
    """Add the engineered columns. Expects the cleaned columns plus a `date` column."""
    d = df.copy()
    d["age_group"] = pd.cut(d["age"], bins=[-1, 12, 18, 35, 50, 65, 200],
                            labels=["child", "teen", "young_adult", "adult", "senior_adult", "elderly"]).astype(str)
    hour = d["appointment_time"]
    d["appointment_period"] = np.select([hour < 10, hour < 13, hour < 16],
                                        ["early_morning", "late_morning", "early_afternoon"], default="late_afternoon")
    d["weather_risk_score"] = d["rainy_day_before"] + d["storm_day_before"]
    d["health_score"] = d[["hipertension", "diabetes", "alcoholism", "handcap"]].sum(axis=1)
    dt = pd.to_datetime(d["date"])
    d["month"] = dt.dt.month
    d["day_of_week"] = dt.dt.dayofweek
    d["is_weekend"] = (d["day_of_week"] >= 5).astype(int)
    return d


def build_appointment_row(inputs, weather_defaults):
    """Turn the values typed into the app into one cleaned + engineered row.

    `inputs` holds: date, appointment_time, age, gender, specialty, place, disability, appointment_shift,
    hipertension, diabetes, alcoholism, handcap, scholarship, sms_received, patient_needs_companion,
    storm_day_before, rain_intensity, heat_intensity.
    `weather_defaults` gives typical temperature / rain figures for each intensity label.
    """
    row = dict(inputs)
    row["under_12_years_old"] = int(row["age"] < 12)
    row["over_60_years_old"] = int(row["age"] >= 60)
    row["age_missing"] = 0
    row["weather_missing"] = 0
    row["rainy_day_before"] = row["storm_day_before"]          # the two flags are identical in 99.9% of the data
    rain = weather_defaults["rain"][row["rain_intensity"]]
    heat = weather_defaults["heat"][row["heat_intensity"]]
    row["average_rain_day"], row["max_rain_day"] = rain["average_rain_day"], rain["max_rain_day"]
    row["average_temp_day"], row["max_temp_day"] = heat["average_temp_day"], heat["max_temp_day"]
    return engineer_features(pd.DataFrame([row]))


def risk_band(probability, threshold):
    """Low / Medium / High from a calibrated no-show probability and the tuned decision threshold."""
    if probability >= threshold:
        return "High"
    if probability >= 0.6 * threshold:
        return "Medium"
    return "Low"


# --------------------------------------------------------------------------------------
# Demand forecasting helpers
# --------------------------------------------------------------------------------------
def build_demand_features(frame, target="y"):
    """Calendar, lag, rolling and weather features for a daily series indexed by date.

    Every lag / rolling value uses only earlier days, so the same function is safe for training
    and for step-by-step (recursive) forecasting.
    """
    f = pd.DataFrame(index=frame.index)
    s = frame[target]
    f["dow"] = frame.index.dayofweek
    f["month"] = frame.index.month
    f["day"] = frame.index.day
    f["woy"] = frame.index.isocalendar().week.astype(int).values
    f["is_weekend"] = (f["dow"] >= 5).astype(int)
    for k in (1, 2, 3, 7, 14):
        f[f"lag_{k}"] = s.shift(k)
    for w in (3, 7, 14, 28):
        f[f"roll_mean_{w}"] = s.shift(1).rolling(w).mean()
    f["roll_std_7"] = s.shift(1).rolling(7).std()
    f["same_dow_4w"] = pd.concat([s.shift(7), s.shift(14), s.shift(21), s.shift(28)], axis=1).mean(axis=1)
    f["ewm_7"] = s.shift(1).ewm(span=7).mean()
    for c in WEATHER_COLS:
        f[c] = frame[c]
    return f


DEMAND_FEATURES = list(build_demand_features(
    pd.DataFrame({"y": np.arange(40.0), **{c: np.zeros(40) for c in WEATHER_COLS}},
                 index=pd.date_range("2020-01-01", periods=40))).columns)


def monthly_weather(history):
    """Typical weather per calendar month (used when no weather forecast is available)."""
    h = history.copy()
    h["month"] = h.index.month
    return h.groupby("month")[WEATHER_COLS].mean()


def recursive_forecast(model, history, future_weather, features, log_target=True, specialty=None, specialty_columns=None):
    """Forecast day by day: each predicted value becomes the lag input for the next day.

    history        DataFrame indexed by date with column `y` and the WEATHER_COLS (last known days)
    future_weather DataFrame indexed by the future dates with the WEATHER_COLS
    specialty      optional name; with `specialty_columns` the one-hot specialty columns are added
    """
    frame = pd.concat([history[["y"] + WEATHER_COLS], future_weather[WEATHER_COLS].assign(y=np.nan)])
    preds = []
    for d in future_weather.index:
        feats = build_demand_features(frame.loc[:d])
        x = feats.iloc[[-1]].copy()
        if specialty_columns is not None:
            for c in specialty_columns:
                x[c] = int(c == f"spec_{specialty}")
        x = x[features]
        yhat = float(model.predict(x)[0])
        yhat = max(float(np.expm1(yhat)) if log_target else yhat, 0.0)
        frame.loc[d, "y"] = yhat
        preds.append(yhat)
    return pd.Series(preds, index=future_weather.index, name="forecast")


def forecast_metrics(y_true, y_pred):
    """MAE, RMSE, R2, MAPE (all days), MAPE (days with at least 50 appointments), WAPE."""
    y = np.asarray(y_true, float)
    p = np.asarray(y_pred, float)
    big = y >= 50
    ss_res, ss_tot = ((y - p) ** 2).sum(), ((y - y.mean()) ** 2).sum()
    return {
        "MAE": float(np.abs(y - p).mean()),
        "RMSE": float(np.sqrt(((y - p) ** 2).mean())),
        "R2": float(1 - ss_res / ss_tot),
        "MAPE_all_days_%": float(100 * np.mean(np.abs(y - p) / np.maximum(y, 1))),
        "MAPE_days_50plus_%": float(100 * np.mean(np.abs(y[big] - p[big]) / y[big])) if big.any() else float("nan"),
        "WAPE_%": float(100 * np.abs(y - p).sum() / y.sum()),
    }
