import datetime
import json
import logging
import time

import requests

from datetime import timezone

from config.settings import (
    CITIES_FILE,
    LOG_DIR,
    LOG_FILE,
    WEATHER_API_URL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    REQUEST_DELAY
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

        return cities

    except FileNotFoundError:

        logging.error(
            "Cities configuration file not found."
        )

        return None

    except json.JSONDecodeError:

        logging.error(
            "Cities configuration contains invalid JSON."
        )

        return None

    except OSError as error:

        logging.error(
            f"Failed to load cities configuration: {error}"
        )

        return None


def test_cities():

    with requests.Session() as session:

        try:

            response = session.get(
                WEATHER_API_URL,
                params={
                    "latitude": 30.0444,
                    "longitude": 31.2357,
                    "current": (
                        "temperature_2m,"
                        "relative_humidity_2m,"
                        "wind_speed_10m"
                    )
                },
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 429:

                logging.warning(
                    "Rate limited during test."
                )

                return False

            if response.status_code >= 500:

                logging.warning(
                    f"Server error {response.status_code} "
                    "during test."
                )

                return False

            response.raise_for_status()

            data = response.json()

            if not data:

                logging.error(
                    "Empty response during test."
                )

                return False

            return True

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout
        ) as error:

            logging.warning(
                f"Network error during test: {error}"
            )

            return False

        except (
            requests.exceptions.RequestException,
            ValueError
        ) as error:

            logging.error(
                f"API test failed: {error}"
            )

            return False


def get_cities(cities):

    failed_cities = []
    cities_list = []

    if not isinstance(cities, list):

        logging.error(
            "Cities input must be a list."
        )

        return cities_list, failed_cities

    with requests.Session() as session:

        for city in cities:

            city_success = False

            required_fields = [
                "city_id",
                "name",
                "lat",
                "lon"
            ]

            missing_fields = [
                field
                for field in required_fields
                if field not in city
            ]

            if missing_fields:

                logging.error(
                    f"City configuration is missing fields: "
                    f"{missing_fields}"
                )

                failed_cities.append(city)

                continue

            for attempt in range(
                1,
                MAX_RETRIES + 1
            ):

                try:

                    response = session.get(
                        WEATHER_API_URL,
                        params={
                            "latitude": city["lat"],
                            "longitude": city["lon"],
                            "current": (
                                "temperature_2m,"
                                "relative_humidity_2m,"
                                "wind_speed_10m"
                            )
                        },
                        timeout=REQUEST_TIMEOUT
                    )

                    if response.status_code == 429:

                        wait_time = (
                            RETRY_DELAY * attempt
                        )

                        logging.warning(
                            f"Rate limited for "
                            f"{city['name']}. "
                            f"Retrying in {wait_time}s..."
                        )

                        time.sleep(wait_time)

                        continue

                    if response.status_code >= 500:

                        logging.warning(
                            f"Server error "
                            f"{response.status_code} "
                            f"for {city['name']}. "
                            f"Retrying..."
                        )

                        time.sleep(
                            RETRY_DELAY
                        )

                        continue

                    response.raise_for_status()

                    data = response.json()

                    current = data.get(
                        "current"
                    )

                    if not isinstance(
                        current,
                        dict
                    ):

                        logging.error(
                            f"Invalid current weather "
                            f"data for {city['name']}."
                        )

                        break

                    raw_record = {
                        "city_id": city["city_id"],
                        "city_name": city["name"],
                        "country": city.get(
                            "country"
                        ),
                        "latitude": city["lat"],
                        "longitude": city["lon"],
                        "temp_celsius": current.get(
                            "temperature_2m"
                        ),
                        "humidity": current.get(
                            "relative_humidity_2m"
                        ),
                        "wind_speed": current.get(
                            "wind_speed_10m"
                        ),
                        "timestamp": current.get(
                            "time"
                        ),
                        "extracted_at": (
                            datetime.datetime.now(
                                timezone.utc
                            ).isoformat()
                        )
                    }

                    cities_list.append(
                        raw_record
                    )

                    city_success = True

                    logging.info(
                        f"Successfully extracted "
                        f"weather data for "
                        f"{city['name']}"
                    )

                    break

                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout
                ) as error:

                    logging.warning(
                        f"Network error on "
                        f"{city['name']}: {error}. "
                        f"Retrying "
                        f"({attempt}/{MAX_RETRIES})..."
                    )

                    time.sleep(
                        RETRY_DELAY
                    )

                except (
                    requests.exceptions.RequestException,
                    ValueError
                ) as error:

                    logging.error(
                        f"Failed to extract "
                        f"{city['name']}: {error}"
                    )

                    break

            if not city_success:

                logging.error(
                    f"Failed to extract "
                    f"{city['name']} after "
                    f"{MAX_RETRIES} attempts."
                )

                failed_cities.append(city)

            time.sleep(
                REQUEST_DELAY
            )

    return cities_list, failed_cities


if __name__ == "__main__":

    cities = load_cities()

    if cities and test_cities():

        successful_data, failed_data = get_cities(
            cities
        )

        logging.info(
            f"Total extracted: "
            f"{len(successful_data)}"
        )

        logging.info(
            f"Total failed: "
            f"{len(failed_data)}"
        )

    else:

        logging.error(
            "Extraction test failed."
        )