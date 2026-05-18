# TideSense

TideSense, liman ve kıyı bölgeleri için gelgit ve su seviyesi takibi yapan, sensör verilerini işleyen, risk seviyesi üreten ve tahminleme katmanı içeren bir izleme platformudur. Proje; FastAPI tabanlı backend, statik frontend, PostgreSQL/TimescaleDB, MQTT veri hattı, arka plan worker süreçleri ve ters proxy bileşenlerinden oluşur.

Bu depo, uygulamanın çalıştırılması, geliştirilmesi ve operasyonel olarak anlaşılması için gereken ana bileşenleri tek yerde toplar.

## Özellikler

- İstasyon bazlı su seviyesi, sıcaklık ve basınç verisi takibi
- MQTT üzerinden anlık telemetri tüketimi
- WebSocket ile canlı veri yayını
- Alarm seviyesi üretimi
- Ay fazı ve astronomik veri işleme
- Makine öğrenmesi tabanlı tahmin altyapısı
- Rol bazlı kullanıcı yönetimi
- CSV benzeri veri dışa aktarma akışları
- Docker Compose ile çok servisli kurulum
- Nginx Proxy Manager ile yayın/proxy katmanı

## Mimari Genel Bakış

Sistem birkaç ana katmandan oluşur:

1. `frontend/`
   Kullanıcının giriş yaptığı ve verileri görüntülediği statik web arayüzü.

2. `backend/`
   FastAPI ile yazılmış REST API, WebSocket, scheduler, servis katmanı, veri modelleri ve iş kuralları burada yer alır.

3. `tidesense-db`
   PostgreSQL + TimescaleDB veritabanı. İlk kurulumda `tidesense_full_db.sql` içeriği ile beslenir.

4. `tidesense-worker`
   MQTT broker’dan telemetri okuyup veritabanına yazan arka plan worker süreci.

5. `tidesense-mqtt`
   Sensör telemetrisi için MQTT broker.

6. `tidesense-proxy`
   Nginx Proxy Manager tabanlı ters proxy ve sertifika yönetim katmanı.

## Veri Akışı

Temel veri akışı şu şekildedir:

1. Sensör ya da simülasyon kaynağı MQTT broker’a veri gönderir.
2. `tidesense-worker`, `tidesense/stations/+/telemetry` desenindeki mesajları dinler.
3. Gelen veri ilgili istasyonla eşleştirilir.
4. Okuma veritabanına kaydedilir.
5. Risk seviyesi hesaplanır.
6. Uygun istemcilere WebSocket üzerinden canlı bildirim gönderilir.
7. Scheduler tarafı tahmin, ay konumu ve dış kaynak veri toplama işlerini periyodik olarak yürütür.

## Teknoloji Yığını

- Backend: FastAPI, SQLAlchemy, Pydantic Settings
- Veritabanı: PostgreSQL, TimescaleDB
- Mesajlaşma: Eclipse Mosquitto MQTT
- Gerçek zamanlı iletişim: WebSocket
- Zamanlayıcı: APScheduler
- ML / veri işleme: pandas, numpy, scikit-learn, joblib
- Astronomi hesapları: ephem, astropy
- Proxy: Nginx Proxy Manager
- Konteyner orkestrasyonu: Docker Compose

## Dizin Yapısı

```text
tidesense/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── ml_artifacts/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── scheduler/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── static/
│   │   ├── websocket/
│   │   └── workers/
│   ├── alembic/
│   ├── requirements.txt
│   ├── worker.py
│   └── run_tests.py
├── frontend/
│   ├── assets/
│   └── index.html
├── npm/
├── docker-compose.yml
├── tidesense_full_db.sql
└── vercel.json
```

## Servisler

`docker-compose.yml` içinde tanımlı ana servisler:

- `tidesense-db`
  PostgreSQL/TimescaleDB veritabanı

- `tidesense-backend`
  FastAPI uygulaması, varsayılan olarak `8000` portunda çalışır

- `tidesense-worker`
  MQTT tüketicisi ve arka plan veri işleyici

- `tidesense-simulator`
  Simülasyon amaçlı veri üretimi için ayrılmış servis tanımı

- `tidesense-frontend`
  Statik frontend dosyalarını yayınlayan servis

- `tidesense-proxy`
  Nginx Proxy Manager, `80`, `81`, `443` portlarını kullanır

- `tidesense-mqtt`
  MQTT broker, `1883` ve `9001` portlarını kullanır

## Gereksinimler

Projeyi Docker ile ayağa kaldırmak için:

- Docker
- Docker Compose

Backend’i yerelde doğrudan çalıştırmak için:

- Python 3.11+
- PostgreSQL erişimi
- MQTT broker erişimi

## Hızlı Başlangıç

### 1. Proje dizinine geçin

```bash
cd /root/tidesense
```

### 2. Backend ortam değişkenlerini hazırlayın

Bu depoda hazır bir `.env.example` dosyası görünmüyor. Bu nedenle `backend/.env` dosyasını sizin oluşturmanız gerekir.

Örnek içerik:

```env
PROJECT_NAME=TideSense API
ENVIRONMENT=development
API_V1_PREFIX=/api/v1
SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=120
JWT_ALGORITHM=HS256

DB_HOST=tidesense-db
DB_PORT=5432
DB_NAME=tidesense
DB_USER=postgres
DB_PASSWORD=tidesense_secret
TIMESCALEDB_ENABLED=true

MQTT_HOST=tidesense-mqtt
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=tidesense

SCHEDULER_ENABLED=true
BOOTSTRAP_HISTORY_HOURS=72
PREDICTION_HORIZON_HOURS=24

ALERT_WARNING_THRESHOLD_CM=120
ALERT_CRITICAL_THRESHOLD_CM=150

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_FROM=tidesense.alert@gmail.com
```

### 3. Servisleri ayağa kaldırın

```bash
docker compose up -d
```

### 4. Servis durumunu kontrol edin

```bash
docker compose ps
```

### 5. Backend erişimini test edin

```bash
curl http://localhost:8000/
```

Beklenen çıktı örneği:

```json
{
  "project": "TideSense API",
  "status": "running",
  "environment": "development",
  "timestamp": "2026-05-18T00:00:00+00:00"
}
```

## Yerel Backend Çalıştırma

Docker dışında backend geliştirmek isterseniz:

```bash
cd /root/tidesense/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Worker’ı ayrı başlatmak için:

```bash
cd /root/tidesense/backend
source .venv/bin/activate
python worker.py
```

## Frontend

Frontend, derlenmiş/statiğe çevrilmiş asset’lerle servis ediliyor. Giriş sayfası `frontend/index.html` üzerinden açılır.

Öne çıkan frontend dosyaları:

- `frontend/index.html`
- `frontend/assets/index-v3.js`
- `frontend/assets/index-bca61955.css`
- `frontend/assets/contact-info.js`
- `frontend/assets/contact-info.css`

Not:
Frontend kaynakları bu depoda okunabilir biçimde değil, büyük ölçüde build çıktısı olarak tutuluyor. Bu nedenle tasarım veya davranış değişikliği yaparken doğrudan asset dosyalarına müdahale ediliyor.

## Backend Bileşenleri

### API

Ana router dosyası:

- `backend/app/api/v1/router.py`

Projede aşağıdaki endpoint grupları bulunur:

- `health`
- `auth`
- `users`
- `stations`
- `ports`
- `sensors`
- `readings`
- `moon`
- `predictions`
- `alerts`
- `cameras`
- `feedback`
- `reports`

### WebSocket

Canlı veri yayını için WebSocket katmanı vardır. MQTT consumer yeni veri aldığında uygun payload’ı WebSocket bağlantılarına iletir.

### Scheduler

`backend/app/scheduler/` altında zamanlanmış işler çalışır. Uygulama başlarken bootstrap süreci tetiklenir ve arka planda periyodik görevler başlatılır.

### Worker

`backend/worker.py` ve `backend/app/workers/mqtt_consumer.py` dosyaları MQTT’den gelen telemetriyi dinler. Beklenen topic yapısı:

```text
tidesense/stations/+/telemetry
```

Beklenen payload örneği:

```json
{
  "station_code": "IST01",
  "recorded_at": "2026-05-18T10:00:00+00:00",
  "water_level_cm": 123.4,
  "air_pressure_hpa": 1012.8,
  "temperature_c": 21.6
}
```

## Veritabanı

Veritabanı ilk kurulumda şu dosyadan yüklenir:

- `tidesense_full_db.sql`

Bu dosya büyük boyutludur ve örnek/veri dolu bir başlangıç kurulumu sağlar. İlk ayağa kaldırma süresi bu nedenle uzayabilir.

Backend tarafında ayrıca şu yapılar vardır:

- SQLAlchemy modelleri
- Alembic migration dosyaları
- `create_database_schema()` bootstrap akışı

Not:
`docker-compose.yml` hem SQL dump importunu hem de uygulama başlatma akışını birlikte kullanır. Bu nedenle temiz kurulumlarda konteynerlerin ilk ayağa kalkışı normalden uzun sürebilir.

## Kimlik Doğrulama ve Yetkilendirme

Backend JWT tabanlı kimlik doğrulama kullanır. Rol bazlı erişim modeli vardır. Test script’inde görülen örnek roller:

- `admin`
- `user`
- `researcher`

Kimlik doğrulama ile ilgili ana ayarlar:

- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `JWT_ALGORITHM`

## Konfigürasyon

Başlıca ortam değişkenleri:

- `PROJECT_NAME`
- `ENVIRONMENT`
- `API_V1_PREFIX`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `TIMESCALEDB_ENABLED`
- `MQTT_HOST`
- `MQTT_PORT`
- `MQTT_TOPIC_PREFIX`
- `SCHEDULER_ENABLED`
- `BOOTSTRAP_HISTORY_HOURS`
- `PREDICTION_HORIZON_HOURS`
- `ALERT_WARNING_THRESHOLD_CM`
- `ALERT_CRITICAL_THRESHOLD_CM`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM`

## Testler

Depoda `backend/run_tests.py` adlı bir test script’i bulunuyor. Bu dosya daha çok entegrasyon/manuel doğrulama tarzı istekler içeriyor.

Çalıştırmak için:

```bash
cd /root/tidesense/backend
python run_tests.py
```

Not:
Bu script çalışan bir backend servisi ve uygun başlangıç verisi bekler. Yani saf unit test mantığında değildir.

## Deployment Notları

### Docker tabanlı dağıtım

Ana dağıtım akışı `docker-compose.yml` üzerinden ilerler.

Önerilen sıralama:

1. `backend/.env` oluşturun
2. Gerekirse SQL dump boyutunu doğrulayın
3. `docker compose up -d` çalıştırın
4. `docker compose logs -f tidesense-backend` ile başlangıç loglarını kontrol edin
5. Proxy yönlendirmelerini Nginx Proxy Manager üzerinden tanımlayın

### Vercel

Depoda `vercel.json` bulunuyor. Bu dosya frontend statik içeriğini Vercel üzerinde yayınlamak için yapılandırılmış.

Ancak mevcut repo yapısında backend ayrı servis olarak ele alındığından, Vercel burada yalnızca frontend dağıtımı için uygundur.

## Operasyonel Notlar

- `tidesense_full_db.sql` dosyası çok büyüktür; taşıma ve ilk kurulum sürelerini etkiler.
- Frontend kaynaklarının önemli bir kısmı derlenmiş asset olarak depoda durur.
- Worker, MQTT broker hazır olana kadar yeniden deneme yapar.
- Backend başlangıcında scheduler bootstrap arka planda tetiklenir.
- Proxy katmanı ayrıca `npm/` altında kendi veri ve sertifika dizinlerini kullanır.

## Geliştirme İçin Öneriler

- `backend/.env.example` dosyası eklenmesi faydalı olur.
- Build edilmemiş frontend kaynaklarının ayrıca depoda tutulması bakım maliyetini düşürür.
- `run_tests.py` dışında gerçek otomatik test paketi eklenmesi önerilir.
- Güvenlik tarafında rate limiting, token iptali ve production HTTPS zorlaması ayrıca gözden geçirilmelidir.

## Sorun Giderme

### Backend açılıyor ama veri gelmiyor

Kontrol edin:

- `tidesense-mqtt` konteyneri çalışıyor mu
- `MQTT_HOST` ve `MQTT_PORT` doğru mu
- MQTT topic yapısı beklenen formatta mı
- İstasyona ait `station_code` veritabanında mevcut mu

### Veritabanı ilk kurulumda uzun sürüyor

Bu beklenen bir durum olabilir. SQL dump boyutu büyük olduğu için ilk init süresi uzar.

### Frontend açılıyor ama API cevap vermiyor

Kontrol edin:

- `tidesense-backend` ayakta mı
- `8000` portu erişilebilir mi
- proxy yönlendirmesi doğru mu
- backend `.env` içindeki veritabanı ayarları geçerli mi

## Lisans

Bu depoda açık bir lisans dosyası görünmüyor. Gerekirse proje sahibi tarafından ayrıca `LICENSE` dosyası eklenmelidir.
