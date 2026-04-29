# TideSense API Reference

Base URL: `/api/v1`

## Authentication

### `POST /api/v1/auth/login`
- Amaç: JWT üretir ve kullanıcı rolünü token içine yazar.
- Body:
```json
{
  "username": "marine_researcher",
  "password": "Research123!"
}
```
- 200 örnek:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 7200,
  "user": {
    "id": 2,
    "username": "marine_researcher",
    "role": "researcher",
    "created_at": "2026-04-24T18:10:00Z"
  }
}
```
- Status codes: `200`, `401`

### `GET /api/v1/auth/me`
- Amaç: Aktif kullanıcı profilini döndürür.
- Auth: `Bearer`
- Status codes: `200`, `401`

## Stations

### `GET /api/v1/stations`
- Amaç: İstasyon listesini döndürür.
- Query: `active_only`
- Status codes: `200`, `401`

### `GET /api/v1/stations/{station_id}`
- Amaç: Tek istasyon detayını döndürür.
- Status codes: `200`, `401`, `404`

## Sensors

### `GET /api/v1/sensors/readings`
- Amaç: Son sensör ölçümlerini listeler.
- Query: `station_id`, `limit`
- Status codes: `200`, `401`

### `GET /api/v1/sensors/latest`
- Amaç: Her istasyon için en güncel sensör kaydını verir.
- Status codes: `200`, `401`

## Readings

### `GET /api/v1/readings/history`
- Amaç: Tarihsel gerçek sensör verisini verir.
- Query:
  - `station_id`
  - `start_at`
  - `end_at`
  - `limit`
  - `export_format=json|csv`
- CSV dışa aktarma için Researcher veya Admin gerekir.
- Status codes: `200`, `400`, `401`, `403`, `404`

### `GET /api/v1/readings/stats`
- Amaç: Belirli periyot için özet istatistik döndürür.
- Query: `station_id`, `period_hours`
- Status codes: `200`, `401`, `404`

### `GET /api/v1/readings/noaa`
- Amaç: DB’ye önceden yazılmış dış kaynak ölçümlerini döndürür.
- Query: `station_id`, `limit`, `refresh`, `provider`
- `provider` değerleri: `mock`, `noaa`, `tidecheck`, `auto`
- `refresh=true` sadece Admin içindir.
- `refresh=true` kullanılırsa cevap içinde `refresh_result` alanı döner ve fallback kullanılıp kullanılmadığı görünür.
- Status codes: `200`, `401`, `403`

## Moon

### `GET /api/v1/moon/current`
- Amaç: Anlık ay fazı, illumination, gravity factor, altitude ve azimuth bilgisi verir.
- Query: `station_id`
- Status codes: `200`, `401`, `404`

## Predictions

### `GET /api/v1/predictions`
- Amaç: İstasyon bazlı 24 saatlik gelgit tahminlerini döndürür.
- Auth: Researcher veya Admin
- Query: `station_id`, `refresh`, `force_retrain`, `horizon_hours`
- Status codes: `200`, `401`, `403`, `404`

## Alerts

### `GET /api/v1/alerts`
- Amaç: Alarm kayıtlarını listeler.
- Query: `station_id`, `severity`, `only_unacknowledged`, `limit`
- Status codes: `200`, `401`

### `POST /api/v1/alerts/ack`
- Amaç: Alarmı okundu olarak işaretler.
- Body:
```json
{
  "alert_id": 12
}
```
- Status codes: `200`, `401`, `404`

## Cameras

### `GET /api/v1/cameras`
- Amaç: İstasyon kamera akışı, snapshot URL, overlay su seviyesi ve risk durumunu döndürür.
- Query: `station_id`
- Status codes: `200`, `401`

## Health

### `GET /api/v1/health`
- Amaç: DB, WebSocket, scheduler ve ML modülü sağlık özetini döndürür.
- Auth: Admin
- Status codes: `200`, `401`, `403`

## Admin Users

### `GET /api/v1/users`
- Amaç: Kullanıcı listesini döndürür.
- Auth: Admin
- Status codes: `200`, `401`, `403`

### `POST /api/v1/users`
- Amaç: Yeni kullanıcı oluşturur.
- Auth: Admin
- Status codes: `201`, `401`, `403`, `409`

## WebSocket

### `WS /ws/live`
- Amaç: Canlı sensör verisi, alarm bildirimi ve bağlantı durumunu iletir.
- Query: `token`
- Mesaj tipleri:
  - `connection`
  - `reading`
  - `alert`
  - `pong`
