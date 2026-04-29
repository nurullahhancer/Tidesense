from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CameraSnapshot(Base):
    __tablename__ = "camera_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), index=True)
    snapshot_url: Mapped[str] = mapped_column(Text)
    detected_water_level_cm: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    risk_status: Mapped[str] = mapped_column(String(16))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    station = relationship("Station", back_populates="camera_snapshots")
