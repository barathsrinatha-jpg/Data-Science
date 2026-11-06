# Medical Appointment No-Show Prediction & Demand Forecasting

A rehabilitation clinic (CER, Brazil) loses about **31.8% of its appointments** to no-shows and struggles to plan
staff for uneven daily demand. This project builds:

1. a **no-show classifier** that gives every appointment a risk score,
2. a **demand forecaster** that predicts daily appointments (overall and per specialty), and
3. a **Streamlit app** that puts both in front of clinic staff.

## Project structure

| File / folder | What it is |
|---|---|
| `Medical_Appointments_Project_Fixed.ipynb` | Full analysis: cleaning, EDA, classifier, forecaster, business impact |
| `medical_utils.py` | Shared feature-engineering and forecasting code used by the notebook **and** the app |
| `app.py` | Streamlit app (3 tabs) |
| `Medical_appointment_data.csv` | Raw data (109,593 appointments, 26 columns) |
| `models/` | Saved models: `no_show_model.joblib`, `demand_overall.joblib`, `demand_specialty.joblib` |
| `reports/` | Result tables (metrics, feature importance, impact scenarios, recommendations) |
| `charts/` | Charts produced by the notebook |
| `requirements.txt` | Python packages |

## How to run

```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace Medical_Appointments_Project_Fixed.ipynb   # about 3 minutes; recreates models/, reports/, charts/
streamlit run app.py
```

The trained models are already included, so you can run `streamlit run app.py` straight away.

## Data cleaning decisions

* **Missing values are kept as information, not hidden.** Blank specialty, disability and city become their own categories
  (`unknown`, `blank`, `MISSING`), because "missing" itself predicts no-shows. Age and weather get a median fill **plus** an
  `age_missing` / `weather_missing` flag. (Filling with the most common value, as in the first version, erased this signal.)
* **City (`place`)**: only 13 values are real cities. About 26,000 other values are made-up names; they are grouped as `OTHER_NAME`.
* Specialty spelling was normalised (`enf` -> nursing, `assist` -> social work, ...).
* Engineered features: age group, appointment period, weather risk score, health score, month, weekday, weekend flag.

## Method

**Classifier.** Stratified 60/20/20 train/validation/test split. Class imbalance is handled with class weights
(`balanced` / `scale_pos_weight`); the decision threshold is tuned on validation data (not left at 0.5); probabilities are
calibrated (isotonic) so a score of 40% really means about 40%. Four models are compared (logistic regression, random forest,
XGBoost, LightGBM). Importance is measured with permutation importance. A time-based split is used as a robustness check.

**Forecaster.** Daily appointment counts with lag, rolling-average, calendar and weather features, split chronologically
(first 80% train, last 20% test). Compared against Ridge, random forest, XGBoost, LightGBM, SARIMAX and simple baselines,
with ablations (no weather / typical weather) and a 1-day vs 7-day horizon test. Per-specialty forecasts use one panel model.

## Results against the project targets

| Model | Metric | Target | Result | Status |
|---|---|---|---|---|
| Classifier | ROC-AUC | > 0.75 | **0.784** | met |
| Classifier | F1, no-show class | > 0.70 | 0.638 | **not met** |
| Classifier | F1, weighted over both classes | > 0.70 | **0.716** | met |
| Forecaster | R² (1 day ahead) | > 0.65 | 0.622 | **not met** |
| Forecaster | MAPE, days with 50+ appointments | < 20% | 47.4% | **not met** |
| Forecaster | MAPE, all days | < 20% | 94% | **not met** |

Classifier on the test set: precision 52%, recall 82%, threshold 0.36. The four models score within 0.03 AUC of each other (LightGBM 0.788 highest on its own);
the final model is XGBoost (scale_pos_weight), picked on validation F1, then calibrated.

**Why the misses are real, not a bug.** Every model tried plateaued near F1 0.64 for the no-show class; the information in the data
is limited (for example, SMS reminders show no effect). Daily demand at this clinic swings from near zero to several hundred
appointments, so percentage error (MAPE) is dominated by quiet days; the total-volume error (WAPE) is about 43%. Forecast quality
also depends on weather: with typical monthly weather instead of real weather, R² falls to about 0.2 (1 day) and 0.07 (7 days).
The forecaster is therefore best used for the next few days, with a weather forecast.

Per-specialty forecasts reach R² 0.63 to 0.66 for the six largest specialties; the small ones (social work, no specialty) are not reliable.

## Business impact

* The **top 49% of appointments by risk** contain **82% of all no-shows**: call those patients instead of everyone.
* If outreach to flagged patients succeeds 10 / 20 / 30% of the time, no-shows fall by **8% / 16% / 25%**
  (31.8% -> 29.2% / 26.6% / 24.0%) while 11,000 fewer calls are needed per 22,000 appointments.
* A staffing planner using this forecast makes about half the daily error of a "last 7 days average" rule
  (81 vs 165 appointments; assumes 10 appointments per specialist per day, which should be replaced with the clinic's real figure).
* Strongest single pattern: appointments whose city is **not one of the 13 real cities miss ~50%** of the time against 9% otherwise.
  This is probably a data-recording artifact and should be checked with the clinic.

Full list of recommendations: `reports/recommendations.csv` and the app's Insights tab.

## Streamlit app

* **No-Show Risk** – enter patient and appointment details (validated inputs) and get a calibrated risk %, risk band and suggested action.
* **Demand Forecast** – choose a start date, number of days, specialty (or all) and weather assumption; get a chart, table,
  staffing estimate and CSV download.
* **Insights & Model Performance** – results vs targets, no-show drivers, demand patterns and recommendations.

## Limitations

* One clinic, one period (data ends 2021-05-12); a model trained here should be re-checked before use elsewhere.
* The data holds no patient identifier, so repeat no-show history (usually a strong signal) cannot be used.
* Forecast accuracy drops quickly beyond a few days and without a weather forecast.
