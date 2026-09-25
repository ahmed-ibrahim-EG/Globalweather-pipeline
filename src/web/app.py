import logging

import pyodbc
from flask import Flask, render_template

from config.settings import (
    DB_SERVER,
    DB_NAME,
    DB_DRIVER,
    DB_TRUSTED_CONNECTION,
    LOG_DIR,
    LOG_FILE,
)



app = Flask(__name__)



LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)



def get_database_connection():
    try:
        connection = pyodbc.connect(
            driver=f"{{{DB_DRIVER}}}",
            server=DB_SERVER,
            database=DB_NAME,
            trusted_connection=DB_TRUSTED_CONNECTION,
        )

        logging.info("Connected to database")
        return connection

    except pyodbc.Error as error:
        logging.error(
            f"Database connection failed: {error}"
        )
        return None


def get_latest_weather():
    connection = get_database_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                CityName,
                Country,
                Latitude,
                Longitude,
                TemperatureC,
                Humidity,
                WindSpeed,
                RecordedAt
            FROM dbo.vw_LatestWeatherByCity
            ORDER BY CityName;
            """
        )

        columns = [
            column[0]
            for column in cursor.description
        ]

        rows = cursor.fetchall()

        weather_data = [
            dict(zip(columns, row))
            for row in rows
        ]

        logging.info(
            f"Retrieved {len(weather_data)} weather records"
        )

        return weather_data

    except pyodbc.Error as error:
        logging.error(
            f"Failed to retrieve weather data: {error}"
        )
        return []

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()



@app.route("/")
def index():
    weather_data = get_latest_weather()

    return render_template(
        "index.html",
        weather_data=weather_data
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )