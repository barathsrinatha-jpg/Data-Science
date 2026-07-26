# 🏥 Medical Appointment No-Show Prediction & Demand Forecasting

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange)
![XGBoost](https://img.shields.io/badge/XGBoost-Latest-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 📌 Project Overview

Healthcare providers often face challenges when patients fail to attend scheduled appointments, leading to inefficient resource utilization, increased operational costs, and longer waiting times for other patients.

This project develops an **end-to-end Machine Learning solution** that addresses two important healthcare problems:

- **Predict whether a patient is likely to miss a scheduled appointment (No-Show Prediction).**
- **Forecast future appointment demand to assist hospitals in resource planning.**

The project follows the complete Data Science lifecycle including:

- Data Loading
- Data Cleaning
- Exploratory Data Analysis (EDA)
- Feature Engineering
- Machine Learning
- Model Evaluation
- Interactive Streamlit Dashboard

---

# 🎯 Project Objectives

## 1. No-Show Prediction

Develop a binary classification model capable of predicting whether a patient will attend or miss a scheduled appointment.

### Business Benefits

- Reduce appointment no-show rates
- Improve hospital scheduling efficiency
- Optimize staff allocation
- Reduce operational costs

---

## 2. Appointment Demand Forecasting

Forecast daily appointment demand to help healthcare administrators anticipate patient volumes.

### Business Benefits

- Improve workforce planning
- Better appointment scheduling
- Resource optimization
- Capacity planning

---

# 📂 Dataset Information

| Property | Value |
|-----------|-------|
| Total Records | **109,557** |
| Original Features | **26** |
| Engineered Features | **11** |
| Final Features | **37** |
| Target Variable | **no_show** |
| Problem Type | Classification & Forecasting |

---

# 🔄 Project Workflow

```text
Raw Dataset
      │
      ▼
Data Loading
      │
      ▼
Data Cleaning
      │
      ▼
Exploratory Data Analysis
      │
      ▼
Feature Engineering
      │
      ├────────────► No-Show Prediction
      │
      └────────────► Demand Forecasting
      │
      ▼
Model Evaluation
      │
      ▼
Streamlit Dashboard
```

---

# 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Scikit-Learn
- XGBoost
- Joblib
- Streamlit

---

# 📊 Exploratory Data Analysis

The following analyses were performed:

- Dataset Profiling
- Missing Value Analysis
- Target Distribution
- Age Distribution
- Gender Distribution
- Specialty Distribution
- Appointment Shift Analysis
- Weather Analysis
- SMS Reminder Analysis
- Correlation Heatmap
- Daily Appointment Trend

---

# ⚙️ Feature Engineering

The following features were engineered to improve model performance.

| Feature | Description |
|----------|-------------|
| age_group | Patient age category |
| no_show_target | Encoded target variable |
| appointment_period | Morning / Afternoon / Evening |
| weather_risk_score | Weather risk indicator |
| health_score | Combined chronic disease score |
| companion_required | Companion requirement flag |
| year | Appointment year |
| month | Appointment month |
| day | Appointment day |
| day_of_week | Day of week |
| week_number | ISO week number |

---

# 🤖 Machine Learning Models

## No-Show Prediction (Classification)

Three classification algorithms were evaluated.

| Model | Purpose |
|--------|----------|
| Logistic Regression | Baseline Model |
| Random Forest | Ensemble Model |
| XGBoost | Final Model |

### Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC

---

## Classification Results

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|--------|----------|-----------|--------|----------|----------|
| Logistic Regression | 71.23% | 57.24% | 37.57% | 45.36% | 74.38% |
| Random Forest | 71.03% | 61.21% | 24.22% | 34.70% | 75.82% |
| **XGBoost** | **72.31%** | **57.77%** | **47.92%** | **52.39%** | **77.31%** |

### ✅ Best Classification Model

**XGBoost Classifier**

---

# 📈 Demand Forecasting

Three regression models were compared for forecasting daily appointment demand.

| Model | Purpose |
|--------|----------|
| Linear Regression | Baseline |
| Random Forest Regressor | Final Model |
| XGBoost Regressor | Comparison |

---

## Forecasting Results

| Model | MAE | RMSE | R² |
|--------|------|------|------|
| Linear Regression | 147.12 | 234.92 | 0.3163 |
| **Random Forest** | **123.42** | **220.39** | **0.3983** |
| XGBoost | 140.33 | 228.80 | 0.3515 |

### ✅ Best Forecasting Model

**Random Forest Regressor**

---

# 📊 Model Evaluation

The following evaluation reports were generated.

## Classification

- Classification Report
- Confusion Matrix
- ROC Curve
- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC

---

## Forecasting

- MAE
- RMSE
- R² Score
- Forecast vs Actual Plot
- Residual Plot

---

# 🖥️ Streamlit Dashboard

The project includes a fully interactive Streamlit dashboard.

## 🏠 Project Overview

- Dataset Summary
- Key Performance Indicators
- Dataset Preview
- Distribution Charts

---

## 🤖 No-Show Prediction

Users can enter patient details and receive:

- Attendance Prediction
- No-Show Prediction
- Prediction Confidence

---

## 📈 Demand Forecasting

Displays

- Historical Appointment Trend
- Forecasted Daily Demand
- Prediction Summary

---

## 📊 Analytics

Displays

- Model Metrics
- Confusion Matrix
- ROC Curve
- Forecast Evaluation
- EDA Visualizations

---

# 📁 Project Structure

```text
Medical-Appointment-NoShow/
│
├── app/
│   └── app.py
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
│
├── models/
│   ├── best_classifier.pkl
│   └── best_forecasting_model.pkl
│
├── reports/
│   ├── eda/
│   └── evaluation/
│
├── src/
│   ├── preprocessing/
│   │   ├── load_data.py
│   │   └── clean_data.py
│   │
│   ├── eda/
│   │   └── eda.py
│   │
│   ├── features/
│   │   └── feature_engineering.py
│   │
│   ├── classification/
│   │   └── train_classifier.py
│   │
│   ├── forecasting/
│   │   └── train_forecasting.py
│   │
│   └── evaluation/
│       └── evaluate_models.py
│
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🚀 Installation

Clone the repository.

```bash
git clone https://github.com/your-username/Medical-Appointment-NoShow.git

cd Medical-Appointment-NoShow
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Project

## Train Classification Model

```bash
python -m src.classification.train_classifier
```

---

## Train Forecasting Model

```bash
python -m src.forecasting.train_forecasting
```

---

## Evaluate Models

```bash
python -m src.evaluation.evaluate_models
```

---

## Launch Streamlit Dashboard

```bash
streamlit run app/app.py
```

---

# 📸 Dashboard Screenshots

> Add screenshots after launching the Streamlit application.

Suggested screenshots:

- Project Overview
- No-Show Prediction
- Demand Forecasting
- Analytics Dashboard

---

# 🔮 Future Improvements

Potential enhancements include:

- Hyperparameter tuning using GridSearchCV or Optuna
- Cross-validation for robust model evaluation
- Multi-day appointment demand forecasting
- Explainable AI using SHAP
- Docker containerization
- FastAPI model deployment
- CI/CD pipeline for automated deployment

---

# 👨‍💻 Author

**Barath Srinath A**

Data Science | Machine Learning | Python | Streamlit | Power BI

---

# ⭐ If you found this project useful, consider giving it a star!