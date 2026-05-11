import cv2
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import STATION_STREAMS
from app.models import CameraSnapshot, SensorReading, Station
from app.services.alert_service import compute_risk_level
from app.services.station_service import list_stations

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
    stations = list_stations(db, active_only=True)
    now = datetime.now(UTC)
    
    for station in stations:
        # Son 1 saat içinde snapshot var mı kontrol et
        exists = db.scalar(
            select(CameraSnapshot.id)
            .where(
                CameraSnapshot.station_id == station.id,
                CameraSnapshot.captured_at >= now - timedelta(hours=1)
            )
            .limit(1)
        )
        if exists:
            continue

        stream_meta = STATION_STREAMS.get(station.code)
        snapshot_path = None
        
        if stream_meta and stream_meta.get("stream_url"):
            snapshot_path = _capture_frame_from_stream(stream_meta["stream_url"], station.code)
            
        # Eğer stream yoksa veya capture başarısızsa varsayılan görseli kullan
        if not snapshot_path:
            snapshot_path = (stream_meta.get("snapshot_url") if stream_meta else None) or \
                            "https://images.unsplash.com/photo-1551244072-5d12893278ab?auto=format&fit=crop&w=960&h=540"

        latest_reading = db.scalar(
            select(SensorReading)
            .where(SensorReading.station_id == station.id)
            .order_by(SensorReading.recorded_at.desc())
            .limit(1)
        )
        
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
    stations = list_stations(db, active_only=True)
    if station_id:
        stations = [s for s in stations if s.id == station_id]
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
                "snapshot_url": "https://images.unsplash.com/photo-1551244072-5d12893278ab?auto=format&fit=crop&w=960&h=540",
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
