"""
=========================================
Module Name : train_classifier.py

Purpose:
Train No Show Classification Models

Project:
Medical Appointment No Show Prediction
=========================================
"""

import joblib
import pandas as pd

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from xgboost import XGBClassifier

from config import PROCESSED_DATA

# ==========================================================
# LOAD DATA
# ==========================================================

def load_dataset():

    filepath = PROCESSED_DATA / "medical_appointments_featured.csv"

    return pd.read_csv(filepath)


# ==========================================================
# PREPARE FEATURES
# ==========================================================

def prepare_data(df):

    df = df.copy()

    drop_columns = [

        "no_show",
        "no_show_target",
        "appointment_date_continuous"

    ]

    X = df.drop(columns=drop_columns)

    y = df["no_show_target"]

    categorical = X.select_dtypes(include=["object", "string"]).columns.tolist()

    numeric = X.select_dtypes(exclude=["object"]).columns.tolist()

    return X, y, categorical, numeric


# ==========================================================
# PREPROCESSOR
# ==========================================================

def create_preprocessor(categorical, numeric):

    numeric_transformer = Pipeline(

        steps=[

            ("imputer", SimpleImputer(strategy="median"))

        ]

    )

    categorical_transformer = Pipeline(

        steps=[

            ("imputer", SimpleImputer(strategy="most_frequent")),

            ("encoder", OneHotEncoder(handle_unknown="ignore"))

        ]

    )

    preprocessor = ColumnTransformer(

        transformers=[

            ("num", numeric_transformer, numeric),

            ("cat", categorical_transformer, categorical)

        ]

    )

    return preprocessor


# ==========================================================
# MODELS
# ==========================================================

def get_models():

    return {

        "Logistic Regression":

            LogisticRegression(

                max_iter=1000,

                random_state=42

            ),

        "Random Forest":

            RandomForestClassifier(

                n_estimators=200,

                random_state=42,

                n_jobs=-1

            ),

        "XGBoost":

            XGBClassifier(
    random_state=42,
    eval_metric="logloss"
)

    }


# ==========================================================
# TRAIN
# ==========================================================

def train_models(X_train, X_test, y_train, y_test, preprocessor):

    results = []

    best_model = None

    best_f1 = 0

    best_name = ""

    for name, model in get_models().items():

        print(f"\nTraining {name}...")

        pipeline = Pipeline(

            steps=[

                ("preprocessor", preprocessor),

                ("classifier", model)

            ]

        )

        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)

        probabilities = pipeline.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, predictions)

        precision = precision_score(y_test, predictions)

        recall = recall_score(y_test, predictions)

        f1 = f1_score(y_test, predictions)

        roc = roc_auc_score(y_test, probabilities)

        results.append({

            "Model": name,

            "Accuracy": round(accuracy, 4),

            "Precision": round(precision, 4),

            "Recall": round(recall, 4),

            "F1 Score": round(f1, 4),

            "ROC AUC": round(roc, 4)

        })

        if f1 > best_f1:

            best_f1 = f1

            best_model = pipeline

            best_name = name

    results_df = pd.DataFrame(results)

    return results_df, best_model, best_name


# ==========================================================
# SAVE MODEL
# ==========================================================

def save_model(model):

    models_folder = Path("models")

    models_folder.mkdir(exist_ok=True)

    filepath = models_folder / "best_classifier.pkl"

    joblib.dump(model, filepath)

    print(f"\nModel saved to {filepath}")


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)

    print("NO SHOW CLASSIFICATION")

    print("=" * 60)

    df = load_dataset()

    X, y, categorical, numeric = prepare_data(df)

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=42,

        stratify=y

    )

    preprocessor = create_preprocessor(

        categorical,

        numeric

    )

    results, best_model, best_name = train_models(

        X_train,

        X_test,

        y_train,

        y_test,

        preprocessor

    )

    print("\n")

    print(results)

    print(f"\nBest Model : {best_name}")

    save_model(best_model)


if __name__ == "__main__":

    main()