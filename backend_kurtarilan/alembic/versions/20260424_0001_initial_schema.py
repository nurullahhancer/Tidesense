"""initial tidesense schema

Revision ID: 20260424_0001
Revises: None
Create Date: 2026-04-24 20:35:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260424_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=False)
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    op.create_table(
        "stations",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("city", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("code", name="uq_stations_code"),
    )
    op.create_index("ix_stations_code", "stations", ["code"], unique=False)

    op.create_table(
        "sensor_readings",
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("station_id", sa.BigInteger(), sa.ForeignKey("stations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("water_level_cm", sa.Numeric(8, 2), nullable=False),
        sa.Column("air_pressure_hpa", sa.Numeric(8, 2), nullable=True),
        sa.Column("temperature_c", sa.Numeric(6, 2), nullable=True),
        sa.Column("data_source", sa.String(length=32), nullable=False, server_default=sa.text("'mock'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("recorded_at", "id", name="pk_sensor_readings"),
    )
    op.create_index(
        "idx_sensor_readings_station_recorded_at",
        "sensor_readings",
        ["station_id", "recorded_at"],
        unique=False,
    )

    op.create_table(
        "noaa_data",
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("station_id", sa.BigInteger(), sa.ForeignKey("stations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("water_level_cm", sa.Numeric(8, 2), nullable=True),
        sa.Column("air_pressure_hpa", sa.Numeric(8, 2), nullable=True),
        sa.Column("temperature_c", sa.Numeric(6, 2), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("recorded_at", "id", name="pk_noaa_data"),
    )
    op.create_index(
        "idx_noaa_data_station_recorded_at",
        "noaa_data",
        ["station_id", "recorded_at"],
        unique=False,
    )

    op.create_table(
        "moon_positions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("moon_phase", sa.String(length=64), nullable=False),
        sa.Column("moon_illumination", sa.Numeric(6, 4), nullable=False),
        sa.Column("gravity_factor", sa.Numeric(10, 6), nullable=False),
        sa.Column("altitude", sa.Numeric(8, 4), nullable=False),
        sa.Column("azimuth", sa.Numeric(8, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_moon_positions_calculated_at", "moon_positions", ["calculated_at"], unique=False)

    op.create_table(
        "tide_predictions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("station_id", sa.BigInteger(), sa.ForeignKey("stations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prediction_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("predicted_water_level_cm", sa.Numeric(8, 2), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index(
        "idx_tide_predictions_station_prediction_time",
        "tide_predictions",
        ["station_id", "prediction_time"],
        unique=False,
    )

    op.create_table(
        "alert_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("station_id", sa.BigInteger(), sa.ForeignKey("stations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_acknowledged", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("acknowledged_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "idx_alert_logs_station_triggered_at",
        "alert_logs",
        ["station_id", "triggered_at"],
        unique=False,
    )
    op.create_index("ix_alert_logs_severity", "alert_logs", ["severity"], unique=False)

    op.create_table(
        "camera_snapshots",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("station_id", sa.BigInteger(), sa.ForeignKey("stations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_url", sa.Text(), nullable=False),
        sa.Column("detected_water_level_cm", sa.Numeric(8, 2), nullable=True),
        sa.Column("risk_status", sa.String(length=16), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "idx_camera_snapshots_station_captured_at",
        "camera_snapshots",
        ["station_id", "captured_at"],
        unique=False,
    )

    op.execute("SELECT create_hypertable('sensor_readings', 'recorded_at', if_not_exists => TRUE)")
    op.execute("SELECT create_hypertable('noaa_data', 'recorded_at', if_not_exists => TRUE)")


def downgrade() -> None:
    op.drop_index("idx_camera_snapshots_station_captured_at", table_name="camera_snapshots")
    op.drop_table("camera_snapshots")

    op.drop_index("ix_alert_logs_severity", table_name="alert_logs")
    op.drop_index("idx_alert_logs_station_triggered_at", table_name="alert_logs")
    op.drop_table("alert_logs")

    op.drop_index("idx_tide_predictions_station_prediction_time", table_name="tide_predictions")
    op.drop_table("tide_predictions")

    op.drop_index("ix_moon_positions_calculated_at", table_name="moon_positions")
    op.drop_table("moon_positions")

    op.drop_index("idx_noaa_data_station_recorded_at", table_name="noaa_data")
    op.drop_table("noaa_data")

    op.drop_index("idx_sensor_readings_station_recorded_at", table_name="sensor_readings")
    op.drop_table("sensor_readings")

    op.drop_index("ix_stations_code", table_name="stations")
    op.drop_table("stations")

    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
