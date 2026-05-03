CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL CHECK (role IN ('user', 'researcher', 'admin', 'super_admin')),
    failed_attempts INTEGER DEFAULT 0,
    lockout_until TIMESTAMPTZ,
    is_blocked BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    last_login_ip VARCHAR(64),
    last_login_user_agent VARCHAR(512),
    last_login_device VARCHAR(128),
    last_login_device_model VARCHAR(128),
    last_login_os VARCHAR(128),
    last_login_browser VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stations (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    code VARCHAR(32) NOT NULL UNIQUE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    city VARCHAR(128) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    recorded_at TIMESTAMPTZ NOT NULL,
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    station_id BIGINT NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    water_level_cm NUMERIC(8, 2) NOT NULL,
    air_pressure_hpa NUMERIC(8, 2),
    temperature_c NUMERIC(6, 2),
    data_source VARCHAR(32) NOT NULL DEFAULT 'mock',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (recorded_at, id)
);

CREATE TABLE IF NOT EXISTS noaa_data (
    recorded_at TIMESTAMPTZ NOT NULL,
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    station_id BIGINT NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    water_level_cm NUMERIC(8, 2),
    air_pressure_hpa NUMERIC(8, 2),
    temperature_c NUMERIC(6, 2),
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (recorded_at, id)
);

CREATE TABLE IF NOT EXISTS moon_positions (
    id BIGSERIAL PRIMARY KEY,
    calculated_at TIMESTAMPTZ NOT NULL,
    moon_phase VARCHAR(64) NOT NULL,
    moon_illumination NUMERIC(6, 4) NOT NULL,
    gravity_factor NUMERIC(10, 6) NOT NULL,
    altitude NUMERIC(8, 4) NOT NULL,
    azimuth NUMERIC(8, 4) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tide_predictions (
    id BIGSERIAL PRIMARY KEY,
    station_id BIGINT NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    prediction_time TIMESTAMPTZ NOT NULL,
    predicted_water_level_cm NUMERIC(8, 2) NOT NULL,
    confidence_score NUMERIC(5, 4) NOT NULL,
    model_version VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alert_logs (
    id BIGSERIAL PRIMARY KEY,
    station_id BIGINT NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    severity VARCHAR(16) NOT NULL CHECK (severity IN ('NORMAL', 'DIKKAT', 'KRITIK')),
    message TEXT NOT NULL,
    triggered_at TIMESTAMPTZ NOT NULL,
    is_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS camera_snapshots (
    id BIGSERIAL PRIMARY KEY,
    station_id BIGINT NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    snapshot_url TEXT NOT NULL,
    detected_water_level_cm NUMERIC(8, 2),
    risk_status VARCHAR(16) NOT NULL CHECK (risk_status IN ('NORMAL', 'DIKKAT', 'KRITIK')),
    captured_at TIMESTAMPTZ NOT NULL
);

SELECT create_hypertable('sensor_readings', 'recorded_at', if_not_exists => TRUE);
SELECT create_hypertable('noaa_data', 'recorded_at', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_station_recorded_at
    ON sensor_readings (station_id, recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_noaa_data_station_recorded_at
    ON noaa_data (station_id, recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_tide_predictions_station_prediction_time
    ON tide_predictions (station_id, prediction_time DESC);

CREATE INDEX IF NOT EXISTS idx_alert_logs_station_triggered_at
    ON alert_logs (station_id, triggered_at DESC);

CREATE INDEX IF NOT EXISTS idx_camera_snapshots_station_captured_at
    ON camera_snapshots (station_id, captured_at DESC);
