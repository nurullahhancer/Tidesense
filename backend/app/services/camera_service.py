import cv2
import os
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import STATION_STREAMS
from app.models import CameraSnapshot, SensorReading, Station
from app.services.alert_service import compute_risk_level

# Snapshot'ları kaydedeceğimiz dizin (Frontend tarafından erişilebilir olmalı)
SNAPSHOT_DIR = Path("app/static/snapshots")
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

def _capture_frame_from_stream(stream_url: str, station_code: str) -> str | None:
    """OpenCV kullanarak stream'den bir kare yakalar ve kaydeder."""
    if not stream_url or "youtube.com" in stream_url or "youtu.be" in stream_url:
        return None
    try:
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            return None
        
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return None
        
        filename = f"{station_code}_{int(datetime.now().timestamp())}.jpg"
        filepath = SNAPSHOT_DIR / filename
        cv2.imwrite(str(filepath), frame)
        cap.release()
        
        # Statik dosya yolunu döndür (Frontend için)
        return f"/static/snapshots/{filename}"
    except Exception:
        return None

def ensure_camera_snapshots(db: Session) -> None:
    stations = list(db.scalars(select(Station).where(Station.is_active.is_(True))).all())
    for station in stations:
        stream_meta = STATION_STREAMS.get(station.code)
        if not stream_meta:
            continue

        latest_reading = db.scalar(
            select(SensorReading)
            .where(SensorReading.station_id == station.id)
            .order_by(SensorReading.recorded_at.desc())
            .limit(1)
        )
        
        # Her saat başı bir kare al
        now = datetime.now(UTC)
        snapshot_path = _capture_frame_from_stream(stream_meta["stream_url"], station.code)
        
        if snapshot_path:
            water_level = float(latest_reading.water_level_cm) if latest_reading else 100.0
            risk = compute_risk_level(water_level)
            
            db.add(
                CameraSnapshot(
                    station_id=station.id,
                    snapshot_url=snapshot_path,
                    detected_water_level_cm=water_level,
                    risk_status=risk,
                    captured_at=now,
                )
            )
    db.commit()


def list_camera_feeds(db: Session, station_id: int | None = None) -> list[dict]:
    query = select(Station).where(Station.is_active.is_(True)).order_by(Station.name.asc())
    if station_id:
        query = query.where(Station.id == station_id)
    stations = list(db.scalars(query).all())
    items = []
    for station in stations:
        snapshot = db.scalar(
            select(CameraSnapshot)
            .where(CameraSnapshot.station_id == station.id)
            .order_by(CameraSnapshot.captured_at.desc())
            .limit(1)
        )
        stream_meta = STATION_STREAMS.get(
            station.code,
            {
                "stream_url": "",
                "snapshot_url": "",
                "resolution": "1280x720",
                "fps": 24,
            },
        )
        items.append(
            {
                "station": station,
                "snapshot_url": snapshot.snapshot_url if snapshot else stream_meta["snapshot_url"],
                "stream_url": stream_meta["stream_url"],
                "detected_water_level_cm": float(snapshot.detected_water_level_cm) if snapshot and snapshot.detected_water_level_cm is not None else None,
                "risk_status": snapshot.risk_status if snapshot else "NORMAL",
                "resolution": stream_meta["resolution"],
                "fps": stream_meta["fps"],
                "captured_at": snapshot.captured_at if snapshot else None,
            }
        )
    return items
