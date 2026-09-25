import logging

from config.settings import LOG_DIR, LOG_FILE



LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def is_valid_record(record):
    errors = []

    if record is None:
        logging.warning("Record is None")
        return False, ["Record is None"]

    if not isinstance(record, dict):
        logging.warning("Record is not a dictionary")
        return False, ["Record must be a dictionary"]


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
        errors.append(
            f"Missing required fields: {missing_fields}"
        )

        return False, errors


    if record["city_name"] is None:
        errors.append("Record has no city name")

    elif not isinstance(record["city_name"], str):
        errors.append("Record has invalid city name type")

    elif not record["city_name"].strip():
        errors.append("Record has empty city name")


    if record["country"] is None:
        errors.append("Record has no country")

    elif not isinstance(record["country"], str):
        errors.append("Record has invalid country type")

    elif not record["country"].strip():
        errors.append("Record has empty country")


    temperature = record["temp_celsius"]

    if temperature is None:
        errors.append("Record has no temperature")

    elif not isinstance(temperature, (int, float)):
        errors.append("Record has invalid temperature type")

    elif not -25 <= temperature <= 60:
        errors.append("Record has out of range temperature")


    humidity = record["humidity"]

    if humidity is not None:

        if not isinstance(humidity, (int, float)):
            errors.append("Record has invalid humidity type")

        elif not 0 <= humidity <= 100:
            errors.append("Record has out of range humidity")



    wind_speed = record["wind_speed"]

    if wind_speed is not None:

        if not isinstance(wind_speed, (int, float)):
            errors.append("Record has invalid wind speed type")

        elif wind_speed < 0:
            errors.append("Record has negative wind speed")



    latitude = record["latitude"]

    if latitude is None:
        errors.append("Record has no latitude")

    elif not isinstance(latitude, (int, float)):
        errors.append("Record has invalid latitude type")

    elif not -90 <= latitude <= 90:
        errors.append("Record has out of range latitude")


    longitude = record["longitude"]

    if longitude is None:
        errors.append("Record has no longitude")

    elif not isinstance(longitude, (int, float)):
        errors.append("Record has invalid longitude type")

    elif not -180 <= longitude <= 180:
        errors.append("Record has out of range longitude")



    if record["timestamp"] is None:
        errors.append("Record has no timestamp")


    if not errors:
        return True, []

    logging.warning(
        f"Record validation failed: {errors}"
    )

    return False, errors