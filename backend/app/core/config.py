from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    project_name: str = Field(default="TideSense API", alias="PROJECT_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    secret_key: str = Field(default="change-this-in-production", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(
        default=120,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="tidesense", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="postgres", alias="DB_PASSWORD")
    timescaledb_enabled: bool = Field(default=True, alias="TIMESCALEDB_ENABLED")

    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        alias="CORS_ORIGINS",
    )

    external_provider: str = Field(default="mock", alias="EXTERNAL_PROVIDER")
    noaa_base_url: str = Field(
        default="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
        alias="NOAA_BASE_URL",
    )
    noaa_station_map: dict[str, str] = Field(default_factory=dict, alias="NOAA_STATION_MAP")
    tidecheck_base_url: str = Field(
        default="https://tidecheck.com",
        alias="TIDECHECK_BASE_URL",
    )
    tidecheck_api_key: str | None = Field(default=None, alias="TIDECHECK_API_KEY")
    tidecheck_datum: str = Field(default="MSL", alias="TIDECHECK_DATUM")
    request_timeout_seconds: int = Field(default=20, alias="REQUEST_TIMEOUT_SECONDS")

    mqtt_host: str = Field(default="localhost", alias="MQTT_HOST")
    mqtt_port: int = Field(default=1883, alias="MQTT_PORT")
    mqtt_topic_prefix: str = Field(default="tidesense", alias="MQTT_TOPIC_PREFIX")

    alert_warning_threshold_cm: float = Field(
        default=120.0,
        alias="ALERT_WARNING_THRESHOLD_CM",
    )
    alert_critical_threshold_cm: float = Field(
        default=150.0,
        alias="ALERT_CRITICAL_THRESHOLD_CM",
    )

    scheduler_enabled: bool = Field(default=True, alias="SCHEDULER_ENABLED")
    moon_update_interval_minutes: int = Field(
        default=5,
        alias="MOON_UPDATE_INTERVAL_MINUTES",
    )
    prediction_interval_minutes: int = Field(
        default=60,
        alias="PREDICTION_INTERVAL_MINUTES",
    )
    alert_check_interval_minutes: int = Field(
        default=5,
        alias="ALERT_CHECK_INTERVAL_MINUTES",
    )
    external_fetch_interval_minutes: int = Field(
        default=60,
        alias="EXTERNAL_FETCH_INTERVAL_MINUTES",
    )

    bootstrap_history_hours: int = Field(default=72, alias="BOOTSTRAP_HISTORY_HOURS")
    prediction_horizon_hours: int = Field(default=24, alias="PREDICTION_HORIZON_HOURS")
    model_artifacts_dir: str = Field(
        default=str(BASE_DIR / "app" / "ml_artifacts"),
        alias="MODEL_ARTIFACTS_DIR",
    )

    frontend_origin: str = Field(default="http://localhost:5173", alias="FRONTEND_ORIGIN")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
