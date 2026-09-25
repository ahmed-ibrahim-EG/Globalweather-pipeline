import time
import logging
import traceback
from datetime import datetime

from config.settings import LOG_DIR, LOG_FILE


RUN_INTERVAL_MINUTES = 60
RETRY_COUNT_ON_FAILURE = 2
RETRY_DELAY_SECONDS = 30



LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def run_stage(stage_name, stage_function):
    attempts = 0

    while attempts <= RETRY_COUNT_ON_FAILURE:
        try:
            logging.info(
                f"Starting stage: {stage_name} "
                f"(attempt {attempts + 1})"
            )

            stage_function()

            logging.info(
                f"Stage succeeded: {stage_name}"
            )

            return True

        except Exception as error:
            attempts += 1

            logging.error(
                f"Stage failed: {stage_name} | Error: {error}"
            )

            logging.error(
                traceback.format_exc()
            )

            if attempts <= RETRY_COUNT_ON_FAILURE:
                logging.info(
                    f"Retrying {stage_name} "
                    f"in {RETRY_DELAY_SECONDS} seconds..."
                )

                time.sleep(RETRY_DELAY_SECONDS)

            else:
                logging.error(
                    f"Stage permanently failed after "
                    f"{attempts} attempts: {stage_name}"
                )

                return False



def run_pipeline_once(pipeline_function):
    run_started_at = datetime.now()

    logging.info(
        f"=== Pipeline run started at {run_started_at} ==="
    )

    success = run_stage(
        "ETL Pipeline",
        pipeline_function
    )

    if not success:
        logging.error(
            "Pipeline stopped because the ETL pipeline failed."
        )
        return False

    logging.info(
        f"=== Pipeline run completed successfully "
        f"at {datetime.now()} ==="
    )

    return True



def main(pipeline_function):
    logging.info("Scheduler started.")

    while True:

        run_pipeline_once(pipeline_function)

        logging.info(
            f"Sleeping for {RUN_INTERVAL_MINUTES} minutes "
            f"until the next run..."
        )

        time.sleep(
            RUN_INTERVAL_MINUTES * 60
        )


if __name__ == "__main__":
    from main import run_pipeline

    main(run_pipeline)