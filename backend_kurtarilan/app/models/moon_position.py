from datetime import datetime

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MoonPosition(Base):
    __tablename__ = "moon_positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    moon_phase: Mapped[str] = mapped_column(String(64))
    moon_illumination: Mapped[float] = mapped_column(Numeric(6, 4))
    gravity_factor: Mapped[float] = mapped_column(Numeric(10, 6))
    altitude: Mapped[float] = mapped_column(Numeric(8, 4))
    azimuth: Mapped[float] = mapped_column(Numeric(8, 4))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
