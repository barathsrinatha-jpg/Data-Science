"""
=========================================
Module Name : evaluate_models.py

Purpose:
Evaluate Classification and Forecasting Models

Project:
Medical Appointment No Show Prediction
=========================================
"""

import joblib
import matplotlib.pyplot as plt
import pandas as pd

from pathlib import Path

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import train_test_split

from config import PROCESSED_DATA


# ==========================================================
# OUTPUT FOLDER
# ==========================================================

OUTPUT = Path("reports") / "evaluation"
OUTPUT.mkdir(parents=True, exist_ok=True)


# ==========================================================
# LOAD DATA
# ==========================================================

def load_data():

    filepath = PROCESSED_DATA / "medical_appointments_featured.csv"

    return pd.read_csv(filepath)


# ==========================================================
# CLASSIFICATION
# ==========================================================

def evaluate_classifier(df):

    print("\nEvaluating Classification Model...")

    model = joblib.load("models/best_classifier.pkl")

    X = df.drop(

        columns=[
            "no_show",
            "no_show_target",
            "appointment_date_continuous"
        ]

    )

    y = df["no_show_target"]

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=42,

        stratify=y

    )

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = pd.DataFrame({

        "Metric": [

            "Accuracy",

            "Precision",

            "Recall",

            "F1 Score",

            "ROC AUC"

        ],

        "Value": [

            accuracy_score(y_test, predictions),

            precision_score(y_test, predictions),

            recall_score(y_test, predictions),

            f1_score(y_test, predictions),

            roc_auc_score(y_test, probabilities)

        ]

    })

    metrics.to_csv(

        OUTPUT / "classification_metrics.csv",

        index=False

    )

    report = classification_report(

        y_test,

        predictions,

        output_dict=True

    )

    pd.DataFrame(report).transpose().to_csv(

        OUTPUT / "classification_report.csv"

    )

    cm = confusion_matrix(

        y_test,

        predictions

    )

    disp = ConfusionMatrixDisplay(cm)

    disp.plot()

    plt.tight_layout()

    plt.savefig(

        OUTPUT / "confusion_matrix.png"

    )

    plt.close()

    RocCurveDisplay.from_predictions(

        y_test,

        probabilities

    )

    plt.tight_layout()

    plt.savefig(

        OUTPUT / "roc_curve.png"

    )

    plt.close()

    print("Classification Evaluation Completed.")


# ==========================================================
# FORECASTING
# ==========================================================

def evaluate_forecasting(df):

    print("\nEvaluating Forecasting Model...")

    model = joblib.load(

        "models/best_forecasting_model.pkl"

    )

    df["appointment_date_continuous"] = pd.to_datetime(

        df["appointment_date_continuous"]

    )

    daily = (

        df.groupby("appointment_date_continuous")

        .size()

        .reset_index(name="appointments")

        .sort_values("appointment_date_continuous")

    )

    daily["day_of_week"] = daily["appointment_date_continuous"].dt.dayofweek

    daily["month"] = daily["appointment_date_continuous"].dt.month

    daily["day"] = daily["appointment_date_continuous"].dt.day

    daily["lag_1"] = daily["appointments"].shift(1)

    daily["lag_7"] = daily["appointments"].shift(7)

    daily["rolling_mean_7"] = daily["appointments"].rolling(7).mean()

    daily = daily.dropna()

    X = daily[

        [

            "day_of_week",

            "month",

            "day",

            "lag_1",

            "lag_7",

            "rolling_mean_7"

        ]

    ]

    y = daily["appointments"]

    split = int(len(daily) * 0.80)

    X_test = X.iloc[split:]

    y_test = y.iloc[split:]

    predictions = model.predict(X_test)

    mse = mean_squared_error(

        y_test,

        predictions

    )

    metrics = pd.DataFrame({

        "Metric": [

            "MAE",

            "RMSE",

            "R2"

        ],

        "Value": [

            mean_absolute_error(

                y_test,

                predictions

            ),

            mse ** 0.5,

            r2_score(

                y_test,

                predictions

            )

        ]

    })

    metrics.to_csv(

        OUTPUT / "forecast_metrics.csv",

        index=False

    )

    plt.figure(figsize=(10,5))

    plt.plot(

        y_test.values,

        label="Actual"

    )

    plt.plot(

        predictions,

        label="Predicted"

    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(

        OUTPUT / "forecast_vs_actual.png"

    )

    plt.close()

    residuals = y_test.values - predictions

    plt.figure(figsize=(8,5))

    plt.scatter(

        predictions,

        residuals

    )

    plt.axhline(

        y=0,

        linestyle="--"

    )

    plt.tight_layout()

    plt.savefig(

        OUTPUT / "forecast_residuals.png"

    )

    plt.close()

    print("Forecast Evaluation Completed.")


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)

    print("MODEL EVALUATION")

    print("=" * 60)

    df = load_data()

    evaluate_classifier(df)

    evaluate_forecasting(df)

    print("\nEvaluation Reports Saved To:")

    print(OUTPUT)


if __name__ == "__main__":

    main()