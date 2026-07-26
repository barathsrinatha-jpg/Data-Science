"""
=========================================
Medical Appointment No Show Prediction
Streamlit Dashboard
=========================================
"""

import joblib
import pandas as pd
import streamlit as st

from pathlib import Path

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(

    page_title="Medical Appointment No Show Prediction",

    page_icon="🏥",

    layout="wide"

)

# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_ROOT / "data" / "processed"

EDA_REPORTS = PROJECT_ROOT / "reports" / "eda"

EVALUATION_REPORTS = PROJECT_ROOT / "reports" / "evaluation"

MODELS = PROJECT_ROOT / "models"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_dataset():

    filepath = PROCESSED_DATA / "medical_appointments_featured.csv"

    return pd.read_csv(filepath)

# --------------------------------------------------
# LOAD MODELS
# --------------------------------------------------

@st.cache_resource
def load_classifier():

    return joblib.load(

        MODELS / "best_classifier.pkl"

    )

@st.cache_resource
def load_forecaster():

    return joblib.load(

        MODELS / "best_forecasting_model.pkl"

    )

df = load_dataset()

classifier = load_classifier()

forecast_model = load_forecaster()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🏥 Medical Appointment Dashboard")

page = st.sidebar.radio(

    "Navigation",

    [

        "Project Overview",

        "No Show Prediction",

        "Demand Forecasting",

        "Analytics"

    ]

)

st.sidebar.markdown("---")

st.sidebar.success("Machine Learning Project")

# --------------------------------------------------
# KPIs
# --------------------------------------------------

TOTAL_APPOINTMENTS = len(df)

NO_SHOW_RATE = (

    (df["no_show_target"] == 1).mean()

) * 100

ATTENDANCE_RATE = (

    (df["no_show_target"] == 0).mean()

) * 100

AVERAGE_AGE = df["age"].mean()

TOTAL_SPECIALTIES = df["specialty"].nunique()
# --------------------------------------------------
# PROJECT OVERVIEW
# --------------------------------------------------

if page == "Project Overview":

    st.title("🏥 Medical Appointment No-Show Prediction Dashboard")

    st.markdown(
        """
        This dashboard demonstrates an end-to-end Machine Learning solution
        for predicting patient no-shows and forecasting appointment demand.
        """
    )

    st.markdown("---")

    # ===============================================
    # KPI CARDS
    # ===============================================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Appointments",
        f"{TOTAL_APPOINTMENTS:,}"
    )

    col2.metric(
        "Attendance Rate",
        f"{ATTENDANCE_RATE:.2f}%"
    )

    col3.metric(
        "No Show Rate",
        f"{NO_SHOW_RATE:.2f}%"
    )

    col4.metric(
        "Average Age",
        f"{AVERAGE_AGE:.1f}"
    )

    col5.metric(
        "Specialties",
        TOTAL_SPECIALTIES
    )

    st.markdown("---")

    # ===============================================
    # DATA PREVIEW
    # ===============================================

    st.subheader("Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

    st.markdown("---")

    # ===============================================
    # AGE DISTRIBUTION
    # ===============================================

    st.subheader("Age Distribution")

    age_counts = df["age_group"].value_counts().sort_index()

    st.bar_chart(age_counts)

    # ===============================================
    # GENDER DISTRIBUTION
    # ===============================================

    st.subheader("Gender Distribution")

    gender_counts = df["gender"].value_counts()

    st.bar_chart(gender_counts)

    st.markdown("---")

    # ===============================================
    # APPOINTMENT SHIFT
    # ===============================================

    st.subheader("Appointment Shift")

    shift_counts = df["appointment_shift"].value_counts()

    st.bar_chart(shift_counts)

    st.markdown("---")

    # ===============================================
    # NO SHOW DISTRIBUTION
    # ===============================================

    st.subheader("No Show Distribution")

    no_show_counts = df["no_show"].value_counts()

    st.bar_chart(no_show_counts)

    st.markdown("---")

    # ===============================================
    # PROJECT INFORMATION
    # ===============================================

    st.subheader("Project Summary")

    summary = pd.DataFrame({

        "Item": [

            "Dataset Size",

            "Features",

            "Classification Model",

            "Forecasting Model",

            "Target Variable"

        ],

        "Value": [

            f"{TOTAL_APPOINTMENTS:,} Records",

            df.shape[1],

            "XGBoost",

            "Random Forest",

            "No Show"

        ]

    })

    st.table(summary)

    st.markdown("---")

    st.success("✅ Data Pipeline Completed")

    st.success("✅ Machine Learning Models Trained")

    st.success("✅ Forecasting Model Developed")

    st.success("✅ Evaluation Completed")
# --------------------------------------------------
# NO SHOW PREDICTION
# --------------------------------------------------

elif page == "No Show Prediction":

    st.title("🤖 No Show Prediction")

    st.write(
        "Enter the patient details below and click **Predict**."
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        age = st.slider(
            "Age",
            0,
            100,
            35
        )

        gender = st.selectbox(
            "Gender",
            sorted(df["gender"].unique())
        )

        specialty = st.selectbox(
            "Specialty",
            sorted(df["specialty"].unique())
        )

        appointment_time = st.slider(
            "Appointment Hour",
            0,
            23,
            10
        )

        appointment_shift = st.selectbox(
            "Appointment Shift",
            sorted(df["appointment_shift"].unique())
        )

        sms_received = st.selectbox(
            "SMS Received",
            [0, 1]
        )

    with col2:

        hipertension = st.selectbox(
            "Hypertension",
            [0, 1]
        )

        diabetes = st.selectbox(
            "Diabetes",
            [0, 1]
        )

        alcoholism = st.selectbox(
            "Alcoholism",
            [0, 1]
        )

        handcap = st.selectbox(
            "Handicap",
            [0, 1]
        )

        scholarship = st.selectbox(
            "Scholarship",
            [0, 1]
        )

        rainy_day_before = st.selectbox(
            "Rainy Day Before",
            [0, 1]
        )

        storm_day_before = st.selectbox(
            "Storm Day Before",
            [0, 1]
        )

    st.markdown("---")

    if st.button("Predict No Show", use_container_width=True):

        weather_risk_score = (
            rainy_day_before +
            storm_day_before
        )

        health_score = (
            hipertension +
            diabetes +
            alcoholism +
            handcap
        )

        if age <= 12:
            age_group = "Child"
        elif age <= 18:
            age_group = "Teen"
        elif age <= 35:
            age_group = "Young Adult"
        elif age <= 50:
            age_group = "Adult"
        elif age <= 65:
            age_group = "Senior Adult"
        else:
            age_group = "Elderly"

        if appointment_time < 10:
            appointment_period = "Morning"
        elif appointment_time < 14:
            appointment_period = "Afternoon"
        else:
            appointment_period = "Evening"

        input_data = pd.DataFrame({

            "specialty": [specialty],
            "appointment_time": [appointment_time],
            "gender": [gender],
            "disability": ["No"],
            "place": [df["place"].mode()[0]],
            "appointment_shift": [appointment_shift],
            "age": [age],
            "under_12_years_old": [1 if age < 12 else 0],
            "over_60_years_old": [1 if age >= 60 else 0],
            "patient_needs_companion": [0],
            "average_temp_day": [df["average_temp_day"].median()],
            "average_rain_day": [df["average_rain_day"].median()],
            "max_temp_day": [df["max_temp_day"].median()],
            "max_rain_day": [df["max_rain_day"].median()],
            "rainy_day_before": [rainy_day_before],
            "storm_day_before": [storm_day_before],
            "rain_intensity": [df["rain_intensity"].mode()[0]],
            "heat_intensity": [df["heat_intensity"].mode()[0]],
            "hipertension": [hipertension],
            "diabetes": [diabetes],
            "alcoholism": [alcoholism],
            "handcap": [handcap],
            "scholarship": [scholarship],
            "sms_received": [sms_received],

            # Engineered Features

            "age_group": [age_group],
            "appointment_period": [appointment_period],
            "weather_risk_score": [weather_risk_score],
            "health_score": [health_score],
            "companion_required": [0],
            "year": [2026],
            "month": [1],
            "day": [1],
            "day_of_week": ["Monday"],
            "week_number": [1]

        })

        prediction = classifier.predict(input_data)[0]

        probability = classifier.predict_proba(
            input_data
        )[0]

        confidence = probability.max() * 100

        st.markdown("---")

        if prediction == 1:

            st.error("⚠️ High Risk of No Show")

        else:

            st.success("✅ Patient Likely To Attend")

        st.metric(

            "Prediction Confidence",

            f"{confidence:.2f}%"

        )

        st.subheader("Input Summary")

        st.dataframe(
            input_data,
            use_container_width=True
        )
# --------------------------------------------------
# DEMAND FORECASTING
# --------------------------------------------------

elif page == "Demand Forecasting":

    st.title("📈 Appointment Demand Forecasting")

    st.write(
        "Forecast daily appointment demand using the trained Random Forest model."
    )

    st.markdown("---")

    daily = (

        df.groupby("appointment_date_continuous")

        .size()

        .reset_index(name="appointments")

    )

    daily["appointment_date_continuous"] = pd.to_datetime(

        daily["appointment_date_continuous"]

    )

    daily = daily.sort_values(

        "appointment_date_continuous"

    )

    st.subheader("Historical Daily Appointments")

    chart = daily.set_index(

        "appointment_date_continuous"

    )

    st.line_chart(

        chart["appointments"]

    )

    st.markdown("---")

    st.subheader("Forecast Next Day")

    latest = daily.copy()

    latest["day_of_week"] = latest["appointment_date_continuous"].dt.dayofweek

    latest["month"] = latest["appointment_date_continuous"].dt.month

    latest["day"] = latest["appointment_date_continuous"].dt.day

    latest["lag_1"] = latest["appointments"].shift(1)

    latest["lag_7"] = latest["appointments"].shift(7)

    latest["rolling_mean_7"] = (

        latest["appointments"]

        .rolling(7)

        .mean()

    )

    latest = latest.dropna()

    latest_row = latest.iloc[-1]

    prediction_input = pd.DataFrame({

        "day_of_week": [

            (latest_row["day_of_week"] + 1) % 7

        ],

        "month": [

            latest_row["month"]

        ],

        "day": [

            latest_row["day"]

        ],

        "lag_1": [

            latest_row["appointments"]

        ],

        "lag_7": [

            latest_row["lag_7"]

        ],

        "rolling_mean_7": [

            latest_row["rolling_mean_7"]

        ]

    })

    prediction = forecast_model.predict(

        prediction_input

    )[0]

    col1, col2 = st.columns(2)

    col1.metric(

        "Predicted Appointments",

        f"{prediction:.0f}"

    )

    col2.metric(

        "Last Recorded Day",

        int(latest_row["appointments"])

    )

    st.markdown("---")

    st.subheader("Forecast Input")

    st.dataframe(

        prediction_input,

        use_container_width=True

    )

    st.markdown("---")

    st.subheader("Forecast Summary")

    forecast_summary = pd.DataFrame({

        "Metric": [

            "Forecast Model",

            "Prediction Horizon",

            "Target"

        ],

        "Value": [

            "Random Forest",

            "Next Day",

            "Daily Appointment Count"

        ]

    })

    st.table(

        forecast_summary

    )

    st.success("Forecast generated successfully.")
# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

elif page == "Analytics":

    st.title("📊 Analytics & Model Performance")

    st.write(
        "Visualizations generated during EDA and model evaluation."
    )

    st.markdown("---")

    # ======================================================
    # CLASSIFICATION METRICS
    # ======================================================

    st.header("Classification Performance")

    metrics_file = EVALUATION_REPORTS / "classification_metrics.csv"

    if metrics_file.exists():

        metrics = pd.read_csv(metrics_file)

        st.dataframe(
            metrics,
            use_container_width=True
        )

    else:

        st.warning("classification_metrics.csv not found.")

    st.markdown("---")

    # ======================================================
    # FORECAST METRICS
    # ======================================================

    st.header("Forecasting Performance")

    forecast_metrics = EVALUATION_REPORTS / "forecast_metrics.csv"

    if forecast_metrics.exists():

        metrics = pd.read_csv(forecast_metrics)

        st.dataframe(
            metrics,
            use_container_width=True
        )

    else:

        st.warning("forecast_metrics.csv not found.")

    st.markdown("---")

    # ======================================================
    # CONFUSION MATRIX
    # ======================================================

    st.header("Confusion Matrix")

    image = EVALUATION_REPORTS / "confusion_matrix.png"

    if image.exists():

        st.image(
            image,
            use_container_width=True
        )

    else:

        st.warning("confusion_matrix.png not found.")

    # ======================================================
    # ROC CURVE
    # ======================================================

    st.header("ROC Curve")

    image = EVALUATION_REPORTS / "roc_curve.png"

    if image.exists():

        st.image(
            image,
            use_container_width=True
        )

    else:

        st.warning("roc_curve.png not found.")

    st.markdown("---")

    # ======================================================
    # FORECAST VS ACTUAL
    # ======================================================

    st.header("Forecast vs Actual")

    image = EVALUATION_REPORTS / "forecast_vs_actual.png"

    if image.exists():

        st.image(
            image,
            use_container_width=True
        )

    else:

        st.warning("forecast_vs_actual.png not found.")

    # ======================================================
    # FORECAST RESIDUALS
    # ======================================================

    st.header("Forecast Residual Plot")

    image = EVALUATION_REPORTS / "forecast_residuals.png"

    if image.exists():

        st.image(
            image,
            use_container_width=True
        )

    else:

        st.warning("forecast_residuals.png not found.")

    st.markdown("---")

    # ======================================================
    # EDA CHARTS
    # ======================================================

    st.header("EDA Visualizations")

    eda_images = [

        "age_distribution.png",

        "gender_distribution.png",

        "appointment_shift.png",

        "target_distribution.png",

        "specialty_distribution.png",

        "weather_analysis.png"

    ]

    for chart in eda_images:

        chart_path = EDA_REPORTS / chart

        if chart_path.exists():

            st.subheader(

                chart.replace("_", " ").replace(".png", "").title()

            )

            st.image(

                chart_path,

                use_container_width=True

            )

    st.markdown("---")

    st.success("Dashboard analytics loaded successfully.")