from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TidePrediction(Base):
    __tablename__ = "tide_predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), index=True)
    prediction_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    predicted_water_level_cm: Mapped[float] = mapped_column(Numeric(8, 2))
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 4))
    model_version: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    station = relationship("Station", back_populates="predictions")
