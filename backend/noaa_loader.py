import argparse
import logging
from datetime import UTC, datetime, timedelta

import sys
from pathlib import Path

# Add backend directory to sys.path so app module can be found
sys.path.append(str(Path(__file__).parent))

from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.models.station import Station
from app.services.external_data_service import fetch_noaa_series

setup_logging()
logger = logging.getLogger("noaa_loader")

def run(hours: int = 24):
    logger.info(f"Starting NOAA data load for the past {hours} hours...")
    db = SessionLocal()
    try:
        stations = db.query(Station).filter(Station.is_active == True).all()
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(hours=hours)

        for station in stations:
            logger.info(f"Fetching NOAA data for station {station.name} (Code: {station.code})")
            result = fetch_noaa_series(station, start_time, end_time)
            if result.used_fallback:
                logger.warning(f"Fallback used for {station.name}. NOAA data might not be available.")
            else:
                logger.info(f"Successfully loaded {result.total_records} records for {station.name}.")
                
        logger.info("NOAA data load completed successfully.")
    except Exception as e:
        logger.error(f"Error during NOAA data load: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TideSense NOAA Data Loader")
    parser.add_argument("--hours", type=int, default=24, help="Number of past hours to fetch")
    args = parser.parse_args()
    run(args.hours)
