"""Clinic Appointment Assistant - Streamlit app

Module 1: No-show risk predictor (takes patient and appointment details, returns a risk score)
Module 2: Demand forecaster (choose a period and a specialty, get expected daily appointments)
Module 3: Insights and model performance

Run from this folder:  streamlit run app.py   (run the notebook first so the models exist)
"""
import math
import os
import time
from datetime import date, timedelta

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import medical_utils as mu

MODEL_DIR, REPORT_DIR, CHART_DIR = "models", "reports", "charts"

st.set_page_config(page_title="Clinic Appointment Assistant", page_icon="🏥", layout="wide")


# --------------------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_models():
    """Load the three saved models once per session."""
    return {
        "risk": joblib.load(f"{MODEL_DIR}/no_show_model.joblib"),
        "overall": joblib.load(f"{MODEL_DIR}/demand_overall.joblib"),
        "specialty": joblib.load(f"{MODEL_DIR}/demand_specialty.joblib"),
    }


@st.cache_data(show_spinner=False)
def read_report(name):
    path = f"{REPORT_DIR}/{name}"
    return pd.read_csv(path) if os.path.exists(path) else None


def show_chart(name, caption=None):
    path = f"{CHART_DIR}/{name}.png"
    if os.path.exists(path):
        st.image(path, caption=caption, width="stretch")
    else:
        st.info(f"Chart '{name}' not found. Run the notebook to create it.")


try:
    models = load_models()
except FileNotFoundError as err:
    st.error("The trained models were not found in the `models/` folder. Run the notebook first, then restart the app.")
    st.caption(str(err))
    st.stop()

risk_bundle, overall, specialty = models["risk"], models["overall"], models["specialty"]
last_date = pd.Timestamp(overall["last_date"])
threshold = risk_bundle["threshold"]
choices = risk_bundle["choices"]


def pretty(value):
    return str(value).replace("_", " ").title()


PLACE_LABEL = {c: pretty(c) if c.isupper() is False else c.title() for c in mu.REAL_CITIES}
PLACE_LABEL[mu.OTHER_PLACE] = "Other place (not one of the 13 cities)"
PLACE_LABEL[mu.MISSING_PLACE] = "Not recorded"
GENDER_LABEL = {"F": "Female", "M": "Male", "I": "Not specified"}
DISABILITY_LABEL = {"intellectual": "Intellectual", "motor": "Motor", "blank": "Not recorded", "missing": "Not recorded"}
ACTIONS = {
    "High": "📞 Call the patient 48 hours before and send a reminder 24 hours before. Offer to reschedule or switch to a "
            "tele-appointment, and consider overbooking this slot.",
    "Medium": "💬 Send a reminder and ask the patient to confirm. Keep the slot, but watch for a late cancellation.",
    "Low": "✅ A standard reminder is enough.",
}
BAND_COLOR = {"High": "#C44E52", "Medium": "#F2A900", "Low": "#2E9E6B"}

# --------------------------------------------------------------------------------------
# Header and sidebar
# --------------------------------------------------------------------------------------
st.title("🏥 Clinic Appointment Assistant")
st.caption("Predict which appointments are likely to be missed, and forecast how many appointments to plan for.")

with st.sidebar:
    st.header("About")
    st.write("Built for the CER rehabilitation clinic, where about **31.8%** of appointments end in a no-show.")
    st.markdown(
        f"**No-show model:** {risk_bundle['model_name']}  \n"
        f"**Demand model:** {overall['model_name']}  \n"
        f"**Data until:** {last_date.date()}"
    )
    st.divider()
    st.caption("Risk scores are probabilities calibrated to the clinic's average no-show rate. Forecasts start after the last day "
               "in the training data.")

tab_risk, tab_forecast, tab_insights = st.tabs(["🩺 No-Show Risk", "📈 Demand Forecast", "📊 Insights & Model Performance"])

# --------------------------------------------------------------------------------------
# Tab 1: no-show risk
# --------------------------------------------------------------------------------------
with tab_risk:
    st.subheader("How likely is this patient to miss the appointment?")
    st.write("Fill in the details below and press **Calculate**. The result is a risk score, a risk band and a suggested action.")

    with st.form("risk_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Patient**")
            age = st.number_input("Age (years)", min_value=0, max_value=110, value=10, step=1)
            gender = st.selectbox("Gender", choices["gender"], format_func=lambda g: GENDER_LABEL.get(g, g))
            disability = st.selectbox("Disability", choices["disability"], format_func=lambda d: DISABILITY_LABEL.get(d, d))
            place = st.selectbox("City", choices["place"], format_func=lambda p: PLACE_LABEL.get(p, p),
                                 help="Choose 'Other place' for a city that is not one of the clinic's 13 cities. "
                                      "In the training data such appointments are missed about half of the time.")
            needs_companion = st.checkbox("Needs a companion", value=True)
        with c2:
            st.markdown("**Appointment**")
            appt_date = st.date_input("Appointment date", value=(last_date + timedelta(days=5)).date(),
                                      min_value=date(2020, 1, 1), max_value=date(2035, 12, 31))
            hmin, hmax = risk_bundle["hour_range"]
            hour = st.slider("Hour of the day", min_value=hmin, max_value=hmax, value=9)
            shift = st.selectbox("Shift", choices["appointment_shift"], format_func=pretty)
            spec = st.selectbox("Specialty", choices["specialty"], format_func=pretty)
            sms = st.checkbox("SMS reminder already sent")
        with c3:
            st.markdown("**Health and background**")
            hypertension = st.checkbox("Hypertension")
            diabetes = st.checkbox("Diabetes")
            alcoholism = st.checkbox("Alcoholism")
            handicap = st.checkbox("Handicap recorded")
            scholarship = st.checkbox("Receives a social benefit (scholarship)")
            st.markdown("**Weather on the day**")
            rain = st.selectbox("Rain", choices["rain_intensity"], index=choices["rain_intensity"].index("no_rain"), format_func=pretty)
            heat = st.selectbox("Temperature", choices["heat_intensity"], index=choices["heat_intensity"].index("mild"), format_func=pretty)
            storm = st.checkbox("Rain/storm flag for the day before", value=True,
                                help="In the training data this flag is 'yes' for 94% of appointments.")
        submitted = st.form_submit_button("Calculate no-show risk", type="primary", width="stretch")

    if submitted:
        problems = []
        if not 0 <= age <= 110:
            problems.append("Age must be between 0 and 110.")
        if appt_date.weekday() >= 5:
            st.warning("This date is a weekend. The clinic's data has fewer appointments on weekends, so treat the score with care.")
        if problems:
            st.error(" ".join(problems))
        else:
            try:
                with st.spinner("Calculating risk..."):
                    t0 = time.perf_counter()
                    row = mu.build_appointment_row({
                        "date": pd.Timestamp(appt_date), "appointment_time": int(hour), "age": float(age), "gender": gender,
                        "specialty": spec, "place": place, "disability": disability, "appointment_shift": shift,
                        "hipertension": int(hypertension), "diabetes": int(diabetes), "alcoholism": int(alcoholism),
                        "handcap": int(handicap), "scholarship": int(scholarship), "sms_received": int(sms),
                        "patient_needs_companion": int(needs_companion), "storm_day_before": int(storm),
                        "rain_intensity": rain, "heat_intensity": heat}, risk_bundle["weather_defaults"])
                    prob = float(risk_bundle["model"].predict_proba(row[risk_bundle["cat_features"] + risk_bundle["num_features"]])[0, 1])
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                band = mu.risk_band(prob, threshold)

                left, right = st.columns([1, 1])
                with left:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number", value=prob * 100, number={"suffix": "%"},
                        title={"text": f"No-show risk: {band}"},
                        gauge={"axis": {"range": [0, 100]}, "bar": {"color": BAND_COLOR[band]},
                               "steps": [{"range": [0, 0.6 * threshold * 100], "color": "#DDF0E6"},
                                         {"range": [0.6 * threshold * 100, threshold * 100], "color": "#FCEFC7"},
                                         {"range": [threshold * 100, 100], "color": "#F6D5D6"}],
                               "threshold": {"line": {"color": "black", "width": 3}, "value": threshold * 100}}))
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=10))
                    st.plotly_chart(fig, width="stretch")
                with right:
                    st.metric("Risk score (probability of a no-show)", f"{prob:.1%}")
                    st.metric("Clinic average", f"{risk_bundle['base_rate']:.1%}", delta=f"{(prob - risk_bundle['base_rate']) * 100:+.1f} points",
                              delta_color="inverse")
                    if band == "High":
                        st.error(f"High risk. {ACTIONS[band]}")
                    elif band == "Medium":
                        st.warning(f"Medium risk. {ACTIONS[band]}")
                    else:
                        st.success(f"Low risk. {ACTIONS[band]}")
                    st.caption(f"The black line marks the decision threshold ({threshold:.0%}): at or above it the model flags the appointment. "
                               f"Computed in {elapsed_ms:.0f} ms.")
                if place == mu.OTHER_PLACE:
                    st.info("The city is not one of the clinic's 13 cities. These records carry a much higher no-show rate in the data; "
                            "check the registration details with the patient.")
                with st.expander("Show the values the model received"):
                    st.dataframe(row.T.rename(columns={0: "value"}).astype(str), width="stretch")
            except Exception as err:   # never show a raw traceback to clinic staff
                st.error("The risk could not be calculated. Please check the inputs and try again.")
                st.caption(f"Technical detail: {err}")

# --------------------------------------------------------------------------------------
# Tab 2: demand forecast
# --------------------------------------------------------------------------------------
with tab_forecast:
    st.subheader("How many appointments should we plan for?")
    st.write(f"The forecast starts after the last recorded day (**{last_date.date()}**) and works day by day, "
             "so accuracy is highest for the first few days.")
    f1, f2, f3, f4 = st.columns([1.3, 1, 1, 1])
    scope = f1.selectbox("Specialty", ["All specialties"] + specialty["specialties"], format_func=pretty)
    start = f2.date_input("Forecast from", value=(last_date + timedelta(days=1)).date(),
                          min_value=(last_date + timedelta(days=1)).date(), max_value=(last_date + timedelta(days=60)).date())
    days = f3.slider("Days to forecast", 1, 28, 14)
    capacity = f4.number_input("Appointments per specialist per day", min_value=1, max_value=60, value=10,
                               help="An assumption used to turn appointments into specialists. Replace it with the clinic's real figure.")

    w1, w2 = st.columns([1, 2])
    weather_mode = w1.radio("Weather assumption", ["Typical for the month", "Custom"], horizontal=False)
    custom = {}
    if weather_mode == "Custom":
        wc = w2.columns(4)
        custom = {"average_temp_day": wc[0].slider("Average temperature (°C)", 8.0, 32.0, 21.0),
                  "average_rain_day": wc[1].slider("Average rain (mm)", 0.0, 3.0, 0.2),
                  "max_rain_day": wc[2].slider("Heaviest rain (mm)", 0.0, 40.0, 2.0),
                  "storm_day_before": 1.0 if wc[3].checkbox("Rain/storm flag", value=True) else 0.0}
    else:
        w2.info("Typical monthly weather is used because no weather forecast is available. "
                "Accuracy is lower than with real weather (see the Insights tab).")

    if st.button("Generate forecast", type="primary"):
        try:
            with st.spinner("Forecasting..."):
                t0 = time.perf_counter()
                end = pd.Timestamp(start) + timedelta(days=days - 1)
                dates = pd.date_range(last_date + timedelta(days=1), end)
                typical = overall["monthly_weather"]
                weather = pd.DataFrame({c: typical.loc[dates.month, c].values for c in mu.WEATHER_COLS}, index=dates)
                for c, v in custom.items():
                    weather[c] = v
                if scope == "All specialties":
                    fc = mu.recursive_forecast(overall["model"], overall["history"], weather, overall["features"], log_target=overall["log_target"])
                    history = overall["history"]["y"]
                else:
                    fc = mu.recursive_forecast(specialty["model"], specialty["histories"][scope], weather, specialty["features"],
                                               log_target=True, specialty=scope, specialty_columns=specialty["specialty_columns"])
                    history = specialty["histories"][scope]["y"]
                fc = fc.loc[pd.Timestamp(start):end]
                elapsed = time.perf_counter() - t0

            table = pd.DataFrame({"Date": fc.index.date, "Weekday": fc.index.day_name(), "Expected appointments": fc.round(0).astype(int).values})
            table["Specialists needed"] = [math.ceil(v / capacity) for v in table["Expected appointments"]]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total expected", f"{int(table['Expected appointments'].sum()):,}")
            m2.metric("Daily average", f"{table['Expected appointments'].mean():.0f}")
            peak = table.loc[table["Expected appointments"].idxmax()]
            m3.metric("Busiest day", f"{peak['Weekday'][:3]} {peak['Date']}", f"{int(peak['Expected appointments'])} appointments", delta_color="off")
            m4.metric("Specialists on the busiest day", int(peak["Specialists needed"]))

            hist = history.loc[last_date - timedelta(days=60):last_date]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist.values, name="Actual (last 60 days)", line=dict(color="#4C72B0")))
            fig.add_trace(go.Scatter(x=fc.index, y=fc.values, name="Forecast", line=dict(color="#C44E52", width=3), mode="lines+markers"))
            fig.add_vline(x=last_date, line_dash="dash", line_color="grey")
            fig.update_layout(title=f"Daily appointments: {pretty(scope) if scope != 'All specialties' else 'all specialties'}",
                              height=420, margin=dict(l=10, r=10, t=50, b=10), yaxis_title="appointments per day",
                              legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, width="stretch")
            st.dataframe(table, width="stretch", hide_index=True)
            st.download_button("Download forecast as CSV", table.to_csv(index=False).encode("utf-8"), "appointment_forecast.csv", "text/csv")
            st.caption(f"Computed in {elapsed * 1000:.0f} ms. Daily volume at this clinic swings widely, so use the forecast as a planning guide, "
                       "not an exact count.")
        except Exception as err:
            st.error("The forecast could not be generated. Please change the inputs and try again.")
            st.caption(f"Technical detail: {err}")

# --------------------------------------------------------------------------------------
# Tab 3: insights
# --------------------------------------------------------------------------------------
with tab_insights:
    sub_results, sub_drivers, sub_patterns, sub_reco = st.tabs(["Model results", "No-show drivers", "Demand patterns", "Recommendations"])

    with sub_results:
        st.subheader("Results against the project targets")
        targets = read_report("targets_vs_results.csv")
        if targets is not None:
            st.dataframe(targets.style.map(lambda v: "color: #2E9E6B; font-weight: bold" if v == "met" else ("color: #C44E52; font-weight: bold" if v == "NOT met" else ""),
                                           subset=["Status"]), width="stretch", hide_index=True)
        metrics = read_report("classification_metrics.csv")
        if metrics is not None:
            m = metrics.set_index(metrics.columns[0])["Test set"]
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("ROC-AUC", f"{m['ROC-AUC']:.3f}")
            k2.metric("F1 (no-show class)", f"{m['F1 (no-show class)']:.2f}")
            k3.metric("Recall", f"{m['Recall']:.0%}")
            k4.metric("Precision", f"{m['Precision']:.0%}")
        st.markdown("**No-show classifier**")
        show_chart("classification_evaluation", "Confusion matrix, ROC, precision-recall, threshold and calibration (test set)")
        comp = read_report("classification_model_comparison.csv")
        if comp is not None:
            st.dataframe(comp, width="stretch", hide_index=True)
        st.markdown("**Demand forecaster**")
        show_chart("forecast_evaluation", "Forecast vs actual on the last 20% of days")
        for name in ("forecast_model_comparison.csv", "forecast_horizon_accuracy.csv", "specialty_forecast_accuracy.csv"):
            df = read_report(name)
            if df is not None:
                st.caption(name.replace(".csv", "").replace("_", " ").capitalize())
                st.dataframe(df, width="stretch", hide_index=True)

    with sub_drivers:
        st.subheader("What drives no-shows?")
        imp = read_report("feature_importance.csv")
        if imp is not None:
            top = imp.head(12).iloc[::-1]
            fig = go.Figure(go.Bar(x=top["importance"], y=top["feature"], orientation="h", marker_color="#C44E52"))
            fig.update_layout(title="Top factors (drop in ROC-AUC when shuffled)", height=420, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, width="stretch")
        c1, c2 = st.columns(2)
        for col, name, title in ((c1, "no_show_by_city.csv", "No-show rate by city group"), (c2, "no_show_by_specialty.csv", "No-show rate by specialty")):
            df = read_report(name)
            if df is not None:
                df = df.sort_values("no_show_rate")
                fig = go.Figure(go.Bar(x=df["no_show_rate"], y=df.iloc[:, 0], orientation="h", marker_color="#4C72B0"))
                fig.update_layout(title=title, height=420, margin=dict(l=10, r=10, t=50, b=10), xaxis_tickformat=".0%")
                col.plotly_chart(fig, width="stretch")
        scen = read_report("impact_scenarios.csv")
        if scen is not None:
            st.markdown("**Estimated no-show reduction from targeting high-risk patients**")
            st.dataframe(scen, width="stretch", hide_index=True)
            st.caption("Assumption: the outreach success rate is the share of flagged patients who would have missed the visit but attend after a call.")
        deciles = read_report("risk_deciles.csv")
        if deciles is not None:
            st.markdown("**No-show rate by risk decile**")
            st.dataframe(deciles.iloc[::-1], width="stretch", hide_index=True)

    with sub_patterns:
        st.subheader("Demand patterns")
        show_chart("eda_daily_demand", "Daily appointments and monthly averages")
        show_chart("eda_demand_patterns", "By weekday, specialty and city")
        show_chart("forecast_by_specialty", "Specialty forecasts on the test period")

    with sub_reco:
        st.subheader("Recommended interventions")
        rec = read_report("recommendations.csv")
        if rec is not None:
            for i, r in rec.iterrows():
                st.markdown(f"**{i + 1}. {r['Recommendation']}**  \n{r['Why (from the data)']}")
        else:
            st.info("Run the notebook to create the recommendations.")
