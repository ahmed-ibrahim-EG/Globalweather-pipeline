import json
import logging

from config.settings import (
    CITIES_FILE,
    LOG_DIR,
    LOG_FILE
)

from src.extract.api_client import get_cities
from src.transform.cleaner import transform_record
from src.validate.quality_checks import is_valid_record
from src.load.loader import load_records


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


def load_cities():

    try:

        with open(
            CITIES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            cities = json.load(file)

        if not isinstance(cities, list):

            logging.error(
                "Cities configuration must be a list."
            )

            return None

        logging.info(
            f"Loaded {len(cities)} cities "
            f"from configuration."
        )

        return cities

    except (
        OSError,
        json.JSONDecodeError
    ) as error:

        logging.error(
            f"Failed to load cities configuration: "
            f"{error}"
        )

        return None


def run_extract(cities):

    logging.info(
        "Starting extraction stage"
    )

    records, failed_cities = get_cities(
        cities
    )

    logging.info(
        f"Extraction completed. "
        f"Successful: {len(records)}, "
        f"Failed: {len(failed_cities)}"
    )

    return records, failed_cities


def run_transform(records):

    logging.info(
        "Starting transformation stage"
    )

    transformed_records = []

    for record in records:

        transformed_record = transform_record(
            record
        )

        if transformed_record is not None:

            transformed_records.append(
                transformed_record
            )

    logging.info(
        f"Transformation completed. "
        f"Records transformed: "
        f"{len(transformed_records)}"
    )

    return transformed_records


def run_validate(records):

    logging.info(
        "Starting validation stage"
    )

    valid_records = []
    invalid_records = []

    for record in records:

        is_valid, errors = is_valid_record(
            record
        )

        if is_valid:

            valid_records.append(record)

        else:

            invalid_records.append(
                {
                    "record": record,
                    "errors": errors
                }
            )

    logging.info(
        f"Validation completed. "
        f"Valid: {len(valid_records)}, "
        f"Invalid: {len(invalid_records)}"
    )

    return valid_records, invalid_records


def run_load(records):

    logging.info(
        "Starting loading stage"
    )

    inserted_count = load_records(
        records
    )

    logging.info(
        f"Loading completed. "
        f"Records inserted: {inserted_count}"
    )

    return inserted_count


def run_pipeline():

    logging.info(
        "================================================"
    )

    logging.info(
        "GlobalWeather Pipeline started"
    )

    logging.info(
        "================================================"
    )

    try:

        cities = load_cities()

        if not cities:

            logging.error(
                "No cities available. "
                "Pipeline stopped."
            )

            return False

        raw_records, failed_cities = run_extract(
            cities
        )

        if not raw_records:

            logging.warning(
                "No records were extracted. "
                "Pipeline stopped."
            )

            return False

        transformed_records = run_transform(
            raw_records
        )

        if not transformed_records:

            logging.warning(
                "No records remained after "
                "transformation. Pipeline stopped."
            )

            return False

        valid_records, invalid_records = (
            run_validate(
                transformed_records
            )
        )

        if not valid_records:

            logging.warning(
                "No valid records available "
                "for loading. Pipeline stopped."
            )

            return False

        inserted_count = run_load(
            valid_records
        )

        logging.info(
            "================================================"
        )

        logging.info(
            f"Pipeline completed successfully. "
            f"Inserted: {inserted_count}, "
            f"Invalid: {len(invalid_records)}, "
            f"Failed cities: {len(failed_cities)}"
        )

        logging.info(
            "================================================"
        )

        return True

    except Exception as error:

        logging.exception(
            f"Pipeline failed unexpectedly: {error}"
        )

        return False


if __name__ == "__main__":

    run_pipeline()