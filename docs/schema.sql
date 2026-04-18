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
-- 4a. Admin Kayıtları
CREATE TABLE IF NOT EXISTS admins (
    adminID    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(25) NOT NULL,
    last_name  VARCHAR(50) NOT NULL,
    passwords  VARCHAR(255) NOT NULL,
    log_time   TIMESTAMPTZ DEFAULT NOW()
);
-- 4b. Researcher Kayıtları
CREATE TABLE IF NOT EXISTS researchers(
    researcherID BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name   VARCHAR(25) NOT NULL,
    last_name    VARCHAR(50) NOT NULL,
    passwords    VARCHAR(255) NOT NULL,
    log_time     TIMESTAMPTZ DEFAULT NOW()
);
-- 4c. User Kayıtları
CREATE TABLE IF NOT EXISTS users(
    userID     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(25) NOT NULL,
    last_name  VARCHAR(50) NOT NULL,
    passwords  VARCHAR(255) NOT NULL,
    log_time   TIMESTAMPTZ DEFAULT NOW()
);

-- TEST KULLANICILARINI EKLİYORUZ (Sisteme giriş yapabilmen için)
INSERT INTO admins(first_name, last_name, passwords) VALUES ('Enes', 'Kaya', 'enes123');
INSERT INTO researchers(first_name, last_name, passwords) VALUES ('Nurullah', 'Hançer', 'nurullah123');
INSERT INTO users(first_name, last_name, passwords) VALUES ('Abdullah', 'Bakit', 'abdullah123');
INSERT INTO admins(first_name, last_name, passwords) VALUES ('Huseyin', 'Kahya', 'huseyini123');
INSERT INTO researchers(first_name, last_name, passwords) VALUES ('Hasan', 'Deniz', 'hasan123');

-- Örnek İndeks (Hızlı sorgu için)
CREATE INDEX IF NOT EXISTS idx_sensor_time ON sensor_readings (sensor_id, time DESC);
