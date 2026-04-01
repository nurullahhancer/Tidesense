-- 1. Sensör Okumaları Tablosu (Time-series)
CREATE TABLE IF NOT EXISTS sensor_readings (
    time        TIMESTAMPTZ       NOT NULL,
    sensor_id   VARCHAR(50)       NOT NULL,
    water_level DOUBLE PRECISION  NOT NULL, -- Su seviyesi (cm/m)
    temperature DOUBLE PRECISION,          -- Opsiyonel: Su sıcaklığı
    humidity    DOUBLE PRECISION           -- Opsiyonel: Nem (sensör sağlığı için)
);

-- TimescaleDB Hypertable Dönüşümü (Zaman bazlı indeksleme için)
SELECT create_hypertable('sensor_readings', 'time', if_not_exists => TRUE);

-- 2. Gelgit Tahminleri Tablosu
CREATE TABLE IF NOT EXISTS tide_predictions (
    prediction_time TIMESTAMPTZ       NOT NULL,
    predicted_level DOUBLE PRECISION  NOT NULL,
    model_version   VARCHAR(50)       NOT NULL,
    confidence      DOUBLE PRECISION           -- Tahmin güven aralığı
);

-- 3. Uyarı/Alarm Kayıtları Tablosu
CREATE TABLE IF NOT EXISTS alert_logs (
    id          SERIAL PRIMARY KEY,
    time        TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
    alert_type  VARCHAR(20)       NOT NULL, -- 'HIGH_TIDE', 'LOW_TIDE', 'SENSOR_FAIL'
    message     TEXT              NOT NULL,
    is_resolved BOOLEAN           DEFAULT FALSE
);

-- Örnek İndeks (Hızlı sorgu için)
CREATE INDEX IF NOT EXISTS idx_sensor_time ON sensor_readings (sensor_id, time DESC);
