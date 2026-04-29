# TideSense Phase 1 Foundation

## Mimari Özeti

TideSense, veri toplama, veri saklama, tahminleme ve görselleştirme katmanlarını birbirinden ayıran monorepo yapısında tasarlanır.

- `frontend/`: React tabanlı dashboard katmanı
- `backend/`: FastAPI tabanlı uygulama servisleri
- `backend/sql`: PostgreSQL + TimescaleDB başlangıç şeması
- `iot_simulator/`: MQTT mantığına uygun test üreticileri
- `docs/`: teknik dokümantasyon ve rapor girdileri

Temel veri akışı şöyledir:

1. NOAA, Tidecheck veya mock kaynaklardan veri toplanır
2. Veri önce PostgreSQL/TimescaleDB'ye yazılır
3. Backend, dashboard isteklerinde yalnızca kendi DB'sinden okur
4. Ay verisi ve geçmiş ölçümlerle tahmin katmanı beslenir
5. Risk ve alarm sonuçları REST + WebSocket ile frontend'e taşınır

## Klasör Yapısı

```text
Tidesense-main/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  │  └─ v1/
│  │  │     └─ endpoints/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  ├─ scheduler/
│  │  ├─ services/
│  │  ├─ websocket/
│  │  └─ workers/
│  ├─ sql/
│  ├─ main.py
│  ├─ worker.py
│  └─ requirements.txt
├─ frontend/
├─ iot_simulator/
├─ mosquitto/
└─ docs/
```

## Veritabanı Tasarımı

Zorunlu tablolar `backend/sql/001_initial_schema.sql` içinde tanımlanmıştır:

- `users`
- `stations`
- `sensor_readings`
- `noaa_data`
- `moon_positions`
- `tide_predictions`
- `alert_logs`
- `camera_snapshots`

TimescaleDB uyumu için:

- `sensor_readings` ve `noaa_data` tabloları hypertable olarak tanımlanır
- yüksek hacimli zaman serisi sorguları için istasyon + zaman indeksleri eklenir
- seed istasyon kayıtları başlangıçta eklenir

## Backend Başlangıç İskeleti

İlk aşamada çalışan omurga aşağıdaki parçaları içerir:

- yapılandırma yönetimi (`app/core/config.py`)
- loglama altyapısı (`app/core/logging.py`)
- SQLAlchemy oturum yönetimi (`app/db/session.py`)
- sağlık endpoint'i (`GET /api/v1/health`)
- scheduler ve websocket yöneticileri için başlangıç sınıfları
- modüler `app/api/v1/endpoints/*` router yapısı

Bu iskelet sonraki aşamalarda ORM, Pydantic, JWT, servisler, scheduler işleri ve WebSocket canlı veri akışı ile genişletilecektir.
