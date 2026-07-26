"""
=========================================
Configuration File
Medical Appointment No Show Prediction
=========================================
"""

from pathlib import Path

# Project Root
BASE_DIR = Path(__file__).resolve().parent

# Data Paths
RAW_DATA = BASE_DIR / "data" / "raw"
CLEAN_DATA = BASE_DIR / "data" / "cleaned"
PROCESSED_DATA = BASE_DIR / "data" / "processed"

# Reports
REPORTS = BASE_DIR / "reports"

# Models
MODELS = BASE_DIR / "models"