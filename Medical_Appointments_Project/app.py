# Streamlit app: Medical appointments (no-show risk + demand forecast)
# Run the notebook first (it saves the models), then:  streamlit run app.py

import math
import os
import time
from datetime import date

import joblib
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Clinic Appointments", layout="wide")


@st.cache_resource
def load_models():
    risk = joblib.load("models/no_show_model.joblib")
    demand = joblib.load("models/demand_models.joblib")
    return risk, demand


risk_info, demand_info = load_models()
last_date = pd.Timestamp(demand_info["last_date"])

st.title("Clinic Appointments Assistant")
st.write("Module 1 predicts the **no-show risk** of an appointment. Module 2 **forecasts** the number of appointments per day.")

tab1, tab2, tab3 = st.tabs(["No-show risk", "Demand forecast", "Insights"])

# ------------------------------------------------------------------ tab 1: no-show risk
with tab1:
    st.subheader("How likely is it that the patient will not come?")
    choices = risk_info["choices"]
    with st.form("risk_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Age", min_value=0, max_value=110, value=10)
            gender = st.selectbox("Gender", choices["gender"], format_func=lambda g: {"F": "Female", "M": "Male", "I": "Other"}.get(g, g))
            disability = st.selectbox("Disability", choices["disability"])
            city = st.selectbox("City", choices["place"],
                                format_func=lambda p: {"other place": "Other place (not one of the 13 cities)", "unknown": "Not known"}.get(p, p.title()))
            companion = st.checkbox("Needs a companion", value=True)
        with c2:
            specialty = st.selectbox("Specialty", choices["specialty"])
            appointment_date = st.date_input("Appointment date", value=date(2021, 5, 20))
            hour = st.slider("Hour of the appointment", 7, 18, 9)
            sms = st.checkbox("SMS reminder sent")
            scholarship = st.checkbox("Has a scholarship")
        with c3:
            st.write("Health conditions")
            hypertension = st.checkbox("Hypertension")
            diabetes = st.checkbox("Diabetes")
            alcoholism = st.checkbox("Alcoholism")
            handicap = st.checkbox("Handicap")
            rain = st.selectbox("Rain", list(risk_info["rain_values"]), index=list(risk_info["rain_values"]).index("no_rain"))
            heat = st.selectbox("Temperature", list(risk_info["heat_values"]), index=list(risk_info["heat_values"]).index("mild"))
            storm = st.checkbox("Storm or rain the day before", value=True)
        submitted = st.form_submit_button("Calculate risk", type="primary")

    if submitted:
        try:
            with st.spinner("Calculating..."):
                start = time.time()
                day = pd.Timestamp(appointment_date)
                row = {"age": age, "age_missing": 0, "appointment_time": hour, "under_12_years_old": int(age < 12),
                       "over_60_years_old": int(age >= 60), "patient_needs_companion": int(companion),
                       "average_temp_day": risk_info["heat_values"][heat]["average_temp_day"],
                       "max_temp_day": risk_info["heat_values"][heat]["max_temp_day"],
                       "average_rain_day": risk_info["rain_values"][rain]["average_rain_day"],
                       "max_rain_day": risk_info["rain_values"][rain]["max_rain_day"],
                       "rainy_day_before": int(storm), "storm_day_before": int(storm),
                       "Hipertension": int(hypertension), "Diabetes": int(diabetes), "Alcoholism": int(alcoholism), "Handcap": int(handicap),
                       "health_score": int(hypertension) + int(diabetes) + int(alcoholism) + int(handicap),
                       "Scholarship": int(scholarship), "SMS_received": int(sms), "month": day.month, "day_of_week": day.dayofweek,
                       "is_weekend": int(day.dayofweek >= 5), "gender": gender, "specialty": specialty, "disability": disability,
                       "place": city, "rain_intensity": rain, "heat_intensity": heat}
                data = pd.get_dummies(pd.DataFrame([row]), columns=risk_info["text_columns"])
                data = data.reindex(columns=risk_info["columns"], fill_value=0).astype(float)     # same columns as in the training
                score = float(risk_info["model"].predict_proba(data)[0, 1])
                seconds = time.time() - start

            if score >= risk_info["high_limit"]:
                level = "High"
            elif score >= risk_info["low_limit"]:
                level = "Medium"
            else:
                level = "Low"

            left, right = st.columns(2)
            with left:
                st.metric("Risk score", str(round(score * 100)) + " %")
                st.progress(score)
                st.write("Risk level: **" + level + "**")
                st.caption("Prediction time: " + str(round(seconds * 1000)) + " ms")
            with right:
                if level == "High":
                    st.error("High risk. Call the patient, send a reminder and think about overbooking this slot.")
                elif level == "Medium":
                    st.warning("Medium risk. Send a reminder and ask the patient to confirm.")
                else:
                    st.success("Low risk. A normal reminder is enough.")
                st.caption("The risk score is not exactly a probability (the model gives more weight to no-shows). "
                           "In the past, about 8% of the Low, 37% of the Medium and 58% of the High risk appointments were no-shows.")
            if day.dayofweek >= 5:
                st.info("This date is a weekend. There are fewer appointments on weekends, so be careful with the result.")
        except Exception as error:
            st.error("The risk could not be calculated. Please check the inputs. (" + str(error) + ")")

# ------------------------------------------------------------------ tab 2: demand forecast
with tab2:
    st.subheader("How many appointments will there be?")
    st.write("The forecast uses the appointments of the days before, the calendar and the weather.")
    c1, c2, c3, c4 = st.columns(4)
    scope = c1.selectbox("Specialty", ["All specialties"] + list(demand_info["specialty_models"]))
    start_after = c2.date_input("Forecast the days after", value=date(2021, 3, 1), min_value=date(2020, 2, 1), max_value=last_date.date())
    days = c3.slider("Number of days", 1, 30, 14)
    capacity = c4.number_input("Appointments per specialist per day", min_value=1, max_value=50, value=10,
                               help="My assumption. The clinic should use its real number.")

    weather_choice = st.radio("Weather for the forecast days", ["Real weather of the data", "Typical weather of the month"], horizontal=True,
                              help="There is no weather forecast in the project, so the real weather is only known for days inside the data.")

    if pd.Timestamp(start_after) > last_date - pd.Timedelta(days=30):
        st.warning("The data has almost no appointments after 2 April 2021 (about 4 per day), so a forecast that starts "
                   "from these days is very low. Choose an earlier date to see a normal forecast.")

    if st.button("Forecast", type="primary"):
        try:
            with st.spinner("Forecasting..."):
                if scope == "All specialties":
                    model, history = demand_info["overall_model"], demand_info["history"]["all"]
                else:
                    model, history = demand_info["specialty_models"][scope], demand_info["history"][scope]
                values = list(history[:pd.Timestamp(start_after)].values)      # appointments until the chosen date
                day, rows = pd.Timestamp(start_after), []
                for _ in range(days):
                    day = day + pd.Timedelta(days=1)
                    if weather_choice.startswith("Real") and day in demand_info["weather_history"].index:
                        weather = demand_info["weather_history"].loc[day].to_dict()
                    else:
                        weather = demand_info["weather_by_month"].loc[day.month].to_dict()      # typical weather of the month
                    features = {"day_of_week": day.dayofweek, "month": day.month, "day_of_month": day.day,
                                "is_weekend": int(day.dayofweek >= 5), "lag_1": values[-1], "lag_7": values[-7],
                                "rolling_7": float(np.mean(values[-7:])), **weather}
                    prediction = max(float(model.predict(pd.DataFrame([features])[demand_info["features"]])[0]), 0)
                    values.append(prediction)         # the prediction is used as "yesterday" for the next day
                    rows.append({"Date": day, "Forecast": round(prediction)})
            result = pd.DataFrame(rows).set_index("Date")
            result["Actual (data)"] = history.reindex(result.index)
            result.loc[result.index > last_date, "Actual (data)"] = np.nan
            result["Weekday"] = result.index.day_name()
            result["Specialists needed"] = [math.ceil(v / capacity) for v in result["Forecast"]]

            m1, m2, m3 = st.columns(3)
            m1.metric("Total forecast", int(result["Forecast"].sum()))
            m2.metric("Average per day", round(result["Forecast"].mean()))
            m3.metric("Specialists needed on the busiest day", int(result["Specialists needed"].max()))
            st.line_chart(result[["Forecast", "Actual (data)"]])
            st.dataframe(result[["Weekday", "Forecast", "Actual (data)", "Specialists needed"]])
            st.download_button("Download the forecast (CSV)", result.to_csv().encode("utf-8"), "forecast.csv", "text/csv")
            st.caption("The final model was trained on all days of the data, so for dates inside the data the forecast looks better "
                       "than it would in real use. For real future days there is no weather forecast, so the typical weather of the month is used.")
        except Exception as error:
            st.error("The forecast could not be made. Please change the inputs. (" + str(error) + ")")

# ------------------------------------------------------------------ tab 3: insights
with tab3:
    st.subheader("Model results")
    c1, c2 = st.columns(2)
    if os.path.exists("reports/classification_results.csv"):
        c1.write("No-show models (test data)")
        c1.dataframe(pd.read_csv("reports/classification_results.csv", index_col=0))
    if os.path.exists("reports/forecast_results.csv"):
        c2.write("Forecast models (last 20% of the days)")
        c2.dataframe(pd.read_csv("reports/forecast_results.csv", index_col=0))

    st.subheader("What matters for no-shows?")
    if os.path.exists("charts/feature_importance.png"):
        st.image("charts/feature_importance.png")
    if os.path.exists("reports/risk_groups.csv"):
        st.write("No-show rate of the risk groups (test data)")
        st.dataframe(pd.read_csv("reports/risk_groups.csv", index_col=0))
    if os.path.exists("reports/business_impact.csv"):
        st.write("Possible reduction of no-shows if the High risk patients are contacted (assumed success rates)")
        st.dataframe(pd.read_csv("reports/business_impact.csv", index_col=0))

    st.subheader("Patterns in the data")
    for image in ["eda_no_show_groups", "eda_daily_demand", "forecast_vs_actual"]:
        if os.path.exists("charts/" + image + ".png"):
            st.image("charts/" + image + ".png")
