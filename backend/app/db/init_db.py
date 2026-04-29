from sqlalchemy import inspect, text

from app.core.logging import get_logger
from app.db.base import Base
from app.db.session import engine
from app.models import (  # noqa: F401
    AlertLog,
    CameraSnapshot,
    MoonPosition,
    NOAAData,
    SensorReading,
    Station,
    TidePrediction,
    User,
)

logger = get_logger(__name__)

EXPECTED_TABLE_COLUMNS = {
    "users": {"id", "username", "password_hash", "role", "created_at"},
    "sensor_readings": {
        "recorded_at",
        "id",
        "station_id",
        "water_level_cm",
        "air_pressure_hpa",
        "temperature_c",
        "data_source",
        "created_at",
    },
    "tide_predictions": {
        "id",
        "station_id",
        "prediction_time",
        "predicted_water_level_cm",
        "confidence_score",
        "model_version",
        "created_at",
    },
    "alert_logs": {
        "id",
        "station_id",
        "severity",
        "message",
        "triggered_at",
        "is_acknowledged",
        "acknowledged_by",
        "acknowledged_at",
    },
}


def repair_legacy_schema() -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        for table_name, expected_columns in EXPECTED_TABLE_COLUMNS.items():
            if table_name not in existing_tables:
                continue

            actual_columns = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            if expected_columns.issubset(actual_columns):
                continue

            legacy_name = f"{table_name}_legacy"
            suffix = 1
            while legacy_name in existing_tables:
                suffix += 1
                legacy_name = f"{table_name}_legacy_{suffix}"

            connection.execute(
                text(f'ALTER TABLE "{table_name}" RENAME TO "{legacy_name}"')
            )
            logger.warning(
                "Legacy table '%s' renamed to '%s' due to schema mismatch",
                table_name,
                legacy_name,
            )
            existing_tables.add(legacy_name)
            existing_tables.discard(table_name)


def ensure_timescaledb_features() -> None:
    with engine.begin() as connection:
        try:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
            connection.execute(
                text(
                    "SELECT create_hypertable('sensor_readings', 'recorded_at', if_not_exists => TRUE)"
                )
            )
            connection.execute(
                text(
                    "SELECT create_hypertable('noaa_data', 'recorded_at', if_not_exists => TRUE)"
                )
            )
            logger.info("TimescaleDB extensions and hypertables ensured")
        except Exception as exc:  # noqa: BLE001
            logger.warning("TimescaleDB features could not be ensured: %s", exc)


def create_database_schema() -> None:
    repair_legacy_schema()
    Base.metadata.create_all(bind=engine)
    ensure_timescaledb_features()
    logger.info("SQLAlchemy metadata ensured")


def verify_database_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connectivity verified successfully")
        return True
    except Exception as exc:
        logger.error("Database connectivity check failed: %s", exc)
        return False
