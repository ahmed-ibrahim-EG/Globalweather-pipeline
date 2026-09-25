import logging
from datetime import datetime

from config.settings import (
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


def clean_missing_value(
    value,
    default=None
):

    if value is None:

        return default

    return value


def classify_climate(
    temp_c
):

    if temp_c is None:

        return None

    if temp_c > 30:

        return "Hot"

    elif temp_c >= 20:

        return "Moderate"

    else:

        return "Cold"


def standardize_city(
    city
):

    if city is None:

        return None

    if not isinstance(
        city,
        str
    ):

        logging.warning(
            f"Invalid city value: {city}"
        )

        return None

    city = city.strip()

    if not city:

        return None

    city = " ".join(
        city.split()
    )

    city = city.title()

    return city


def convert_timestamp(
    timestamp
):

    if timestamp is None:

        return None

    if isinstance(
        timestamp,
        datetime
    ):

        return timestamp

    if not isinstance(
        timestamp,
        str
    ):

        logging.warning(
            f"Invalid timestamp value: {timestamp}"
        )

        return None

    try:

        return datetime.fromisoformat(
            timestamp
        )

    except ValueError:

        logging.warning(
            f"Invalid timestamp format: {timestamp}"
        )

        return None


def transform_record(
    raw_record
):

    if raw_record is None:

        return None

    if not isinstance(
        raw_record,
        dict
    ):

        logging.warning(
            "Invalid raw record. "
            "Expected dictionary."
        )

        return None

    required_fields = {
        "city_id",
        "city_name",
        "country",
        "latitude",
        "longitude",
        "temp_celsius",
        "humidity",
        "wind_speed",
        "timestamp"
    }

    missing_fields = (
        required_fields
        - raw_record.keys()
    )

    if missing_fields:

        logging.warning(
            "Record is missing required "
            f"fields: {missing_fields}"
        )

        return None

    transformed_record = (
        raw_record.copy()
    )

    city = standardize_city(
        transformed_record[
            "city_name"
        ]
    )

    if city is None:

        logging.warning(
            "Record rejected because "
            "city name is invalid."
        )

        return None

    transformed_record[
        "city_name"
    ] = city

    transformed_record[
        "humidity"
    ] = clean_missing_value(
        transformed_record[
            "humidity"
        ]
    )

    transformed_record[
        "wind_speed"
    ] = clean_missing_value(
        transformed_record[
            "wind_speed"
        ]
    )

    transformed_record[
        "timestamp"
    ] = convert_timestamp(
        transformed_record[
            "timestamp"
        ]
    )

    if transformed_record[
        "timestamp"
    ] is None:

        logging.warning(
            f"Record rejected because "
            f"timestamp is invalid for "
            f"{transformed_record['city_name']}."
        )

        return None

    transformed_record[
        "climate"
    ] = classify_climate(
        transformed_record[
            "temp_celsius"
        ]
    )

    return transformed_record