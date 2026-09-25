import logging

import pyodbc

from config.settings import (
    DB_SERVER,
    DB_NAME,
    DB_DRIVER,
    DB_TRUSTED_CONNECTION,
    LOG_DIR,
    LOG_FILE
)


LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)


def connect_to_database():

    try:

        connection = pyodbc.connect(
            driver=f"{{{DB_DRIVER}}}",
            server=DB_SERVER,
            database=DB_NAME,
            trusted_connection=DB_TRUSTED_CONNECTION
        )

        logging.info(
            "Connected to database"
        )

        return connection

    except pyodbc.Error as error:

        logging.error(
            f"Database connection failed: {error}"
        )

        return None


def load_records(records):

    if not records:

        logging.warning(
            "No records to load"
        )

        return 0

    connection = connect_to_database()

    if connection is None:

        return 0

    inserted_count = 0
    skipped_count = 0

    cursor = None

    try:

        cursor = connection.cursor()

        check_sql = """
            SELECT 1
            FROM dbo.WeatherReadings
            WHERE CityName = ?
              AND RecordedAt = ?
        """

        insert_sql = """
            INSERT INTO dbo.WeatherReadings
            (
                CityName,
                Country,
                Latitude,
                Longitude,
                TemperatureC,
                Humidity,
                WindSpeed,
                RecordedAt
            )
            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
        """

        for record in records:

            required_fields = [
                "city_name",
                "country",
                "latitude",
                "longitude",
                "temp_celsius",
                "humidity",
                "wind_speed",
                "timestamp"
            ]

            missing_fields = [
                field
                for field in required_fields
                if field not in record
            ]

            if missing_fields:

                logging.warning(
                    f"Record skipped. "
                    f"Missing fields: {missing_fields}"
                )

                skipped_count += 1

                continue

            cursor.execute(
                check_sql,
                record["city_name"],
                record["timestamp"]
            )

            existing_record = cursor.fetchone()

            if existing_record:

                logging.info(
                    f"Duplicate record skipped "
                    f"for {record['city_name']}"
                )

                skipped_count += 1

                continue

            cursor.execute(
                insert_sql,
                record["city_name"],
                record["country"],
                record["latitude"],
                record["longitude"],
                record["temp_celsius"],
                record["humidity"],
                record["wind_speed"],
                record["timestamp"]
            )

            inserted_count += 1

            logging.info(
                f"Weather record inserted "
                f"for {record['city_name']}"
            )

        connection.commit()

        logging.info(
            f"Loading completed. "
            f"Inserted: {inserted_count}, "
            f"Skipped: {skipped_count}"
        )

        return inserted_count

    except pyodbc.Error as error:

        connection.rollback()

        logging.error(
            f"Loading failed. "
            f"Transaction rolled back: {error}"
        )

        return 0

    finally:

        if cursor is not None:

            cursor.close()

        connection.close()

        logging.info(
            "Database connection closed"
        )