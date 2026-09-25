# ============================================================
# config/settings.py
# Centralized project configuration
# ============================================================

import os

from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# ADDED — Load .env
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ============================================================
# ADDED — API Configuration
# ============================================================

WEATHER_API_URL = os.getenv(
    "WEATHER_API_URL",
    "https://api.open-meteo.com/v1/forecast"
)


# ============================================================
# ADDED — Cities Configuration
# ============================================================

CITIES_FILE = BASE_DIR / "config" / "cities.json"


# ============================================================
# ADDED — Logging Configuration
# ============================================================

LOG_DIR = BASE_DIR / "logs"

LOG_FILE = LOG_DIR / "pipeline.log"


# ============================================================
# ADDED — Database Configuration
# ============================================================

DB_SERVER = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")

DB_NAME = os.getenv(
    "DB_NAME",
    "GlobalWeatherDB"
)

DB_DRIVER = os.getenv(
    "DB_DRIVER",
    "ODBC Driver 17 for SQL Server"
)

DB_TRUSTED_CONNECTION = os.getenv(
    "DB_TRUSTED_CONNECTION",
    "yes"
)


# ============================================================
# ADDED — Extraction Configuration
# ============================================================

REQUEST_TIMEOUT = int(
    os.getenv("REQUEST_TIMEOUT", "10")
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "3")
)

RETRY_DELAY = int(
    os.getenv("RETRY_DELAY", "2")
)

REQUEST_DELAY = float(
    os.getenv("REQUEST_DELAY", "0.1")
)