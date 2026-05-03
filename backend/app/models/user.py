from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), index=True)
    
    failed_attempts: Mapped[int] = mapped_column(default=0)
    lockout_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_login_user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    last_login_device: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_login_os: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_login_browser: Mapped[str | None] = mapped_column(String(128), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    acknowledged_alerts = relationship("AlertLog", back_populates="acknowledged_by_user")
