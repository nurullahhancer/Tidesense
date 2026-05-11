import json
import time
from datetime import UTC, datetime

import paho.mqtt.client as mqtt
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.session import SessionLocal
from app.models import SensorReading, Station
from app.services.alert_service import compute_risk_level
from app.websocket.manager import connection_manager

setup_logging()
logger = get_logger(__name__)


def _topic_for_station() -> str:
    return f"{settings.mqtt_topic_prefix}/stations/+/telemetry"


def on_message(client, userdata, msg) -> None:  # noqa: ANN001
    try:
        payload = json.loads(msg.payload.decode())
        station_code = payload["station_code"]
        db = SessionLocal()
        try:
            station = db.scalar(select(Station).where(Station.code == station_code))
            if station is None:
                logger.warning("Received MQTT data for unknown station: %s", station_code)
                return
            reading = SensorReading(
                station_id=station.id,
                recorded_at=datetime.fromisoformat(payload["recorded_at"]).astimezone(UTC),
                water_level_cm=payload["water_level_cm"],
                air_pressure_hpa=payload.get("air_pressure_hpa"),
                temperature_c=payload.get("temperature_c"),
                data_source="mqtt",
            )
            db.add(reading)
            db.commit()
            risk = compute_risk_level(float(reading.water_level_cm))
            connection_manager.emit(
                {
                    "type": "reading",
                    "payload": {
                        "station_id": station.id,
                        "station_code": station.code,
                        "water_level_cm": float(reading.water_level_cm),
                        "air_pressure_hpa": float(reading.air_pressure_hpa) if reading.air_pressure_hpa is not None else None,
                        "temperature_c": float(reading.temperature_c) if reading.temperature_c is not None else None,
                        "recorded_at": reading.recorded_at.isoformat(),
                        "risk_level": risk,
                    },
                }
            )
            logger.info("MQTT reading stored for %s", station.code)
        finally:
            db.close()
    except Exception as exc:  # noqa: BLE001
        logger.error("MQTT message processing failed: %s", exc)


def run_worker() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message

    connected = False
    while not connected:
        try:
            client.connect(settings.mqtt_host, settings.mqtt_port, 60)
            connected = True
        except Exception:  # noqa: BLE001
            logger.warning("MQTT broker not ready, retrying in 5 seconds")
            time.sleep(5)

    topic = _topic_for_station()
    client.subscribe(topic)
    logger.info("MQTT consumer listening on %s", topic)
    client.loop_forever()
