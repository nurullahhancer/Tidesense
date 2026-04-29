# TideSense

TideSense, kıyı istasyonları için gelgit, su seviyesi, ay konumu, basınç, sıcaklık, kamera görüntüsü ve risk durumunu izleyen; aynı zamanda 24 saatlik tahmin üreten tam yığın bir demo projedir.

## Teknoloji Yığını

- Backend: FastAPI + SQLAlchemy + APScheduler + scikit-learn
- Frontend: React + React Router + Recharts + Leaflet
- Veritabanı: PostgreSQL + TimescaleDB
- Kimlik doğrulama: JWT
- Gerçek zamanlı katman: WebSocket
- IoT akışı: MQTT uyumlu worker + istasyon simülatörü
- Konteynerleşme: Docker + Docker Compose

## Dış Veri Katmanı

- `EXTERNAL_PROVIDER=mock|tidecheck|noaa|auto` ile provider seçilebilir.
- `tidecheck` seçildiğinde gerçek HTTP çağrısı denenir; tarih/plan sınırı veya anahtar sorunu varsa kontrollü mock fallback kullanılır.
- `noaa` seçildiğinde `NOAA_STATION_MAP` ile istasyon dış ID eşlemesi verilirse resmi NOAA Data API çağrılır.
- Dashboard hiçbir zaman dış API’ye doğrudan gitmez; veri önce DB’ye yazılır, sonra frontend yalnızca backend’den okur.

## Klasörler

- `backend/`: API, servisler, scheduler, websocket, model katmanı
- `frontend/`: dark-theme dashboard, login, grafikler ve harita
- `iot_simulator/`: MQTT üzerinden istasyon telemetrisi üreten servis
- `docs/`: mimari ve API referansı
- `mosquitto/`: broker yapılandırması

## Demo Kullanıcıları

- `coastal_user` / `User123!`
- `marine_researcher` / `Research123!`
- `system_admin` / `Admin123!`

## Docker ile Çalıştırma

1. Kök dizinde `.env.example` dosyasını `.env` olarak kopyalayın.
2. Gerekirse `TIDECHECK_API_KEY` alanına kendi anahtarınızı ekleyin.
3. Aşağıdaki komutu çalıştırın:

```bash
docker compose up --build
```

Servisler:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- TimescaleDB: `localhost:5432`
- MQTT Broker: `localhost:1883`

## Yerel Geliştirme

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### Worker

```bash
cd backend
python worker.py
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

### IoT Simulator

```bash
cd iot_simulator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python simulator.py
```

## Veritabanı ve Migration

- Başlangıç TimescaleDB şeması: `backend/sql/001_initial_schema.sql`
- Alembic yapısı ve ilk revision: `backend/alembic.ini` ve `backend/alembic/versions/20260424_0001_initial_schema.py`
- ORM metadata yerel geliştirmede uygulama açılışında da oluşturulur

## API Referansı

Detaylı endpoint açıklamaları ve örnek payloadlar için:

- `docs/api-reference.md`
- `docs/phase-1-foundation.md`
