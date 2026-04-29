from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.alert_service import evaluate_all_stations
from app.services.camera_service import ensure_camera_snapshots
from app.services.external_data_service import refresh_recent_external_data
from app.services.moon_service import record_moon_snapshot
from app.services.prediction_service import generate_predictions_for_all_stations, train_models_for_all_stations
from app.services.seed_service import bootstrap_initial_data


def _with_session(action) -> None:
    db: Session = SessionLocal()
    try:
        action(db)
    finally:
        db.close()


def bootstrap_job() -> None:
    def action(db: Session) -> None:
        bootstrap_initial_data(db)
        record_moon_snapshot(db)
        train_models_for_all_stations(db)
        generate_predictions_for_all_stations(db)
        evaluate_all_stations(db)
        ensure_camera_snapshots(db)

    _with_session(action)


def moon_update_job() -> None:
    _with_session(lambda db: record_moon_snapshot(db))


import logging
logger = logging.getLogger(__name__)

def external_fetch_job() -> None:
    def action(db: Session) -> None:
        try:
            # 1. Dış veriyi çek (Tidecheck / NOAA)
            refresh_recent_external_data(db)
        except Exception as e:
            logger.error(f"Error fetching external data: {e}", exc_info=True)
            
        try:
            # 2. Kameraları kontrol et
            ensure_camera_snapshots(db)
        except Exception as e:
            logger.error(f"Error checking cameras: {e}", exc_info=True)
            
        try:
            # 3. ML modelini yeni verilerle veya fallback ile eğit
            train_models_for_all_stations(db)
        except Exception as e:
            logger.error(f"Error training models: {e}", exc_info=True)
            
        try:
            # 4. Alarmları kontrol et
            evaluate_all_stations(db)
        except Exception as e:
            logger.error(f"Error evaluating alerts: {e}", exc_info=True)

    _with_session(action)


def prediction_generation_job() -> None:
    _with_session(lambda db: generate_predictions_for_all_stations(db))


def alert_check_job() -> None:
    def action(db: Session) -> None:
        evaluate_all_stations(db)
        ensure_camera_snapshots(db)

    _with_session(action)
