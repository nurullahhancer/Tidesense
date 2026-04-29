from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Identity, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NOAAData(Base):
    __tablename__ = "noaa_data"

    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), index=True)
    water_level_cm: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    air_pressure_hpa: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    temperature_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    station = relationship("Station", back_populates="noaa_records")
