# TideSense: Ay Konumuna Dayalı Akıllı Gelgit İzleme ve Tahmin Sistemi

## Proje Hakkında
TideSense, gerçek zamanlı IoT verileri, astronomik hesaplamalar ve makine öğrenmesini birleştirerek yüksek doğruluklu gelgit tahmini yapan bir sistemdir.

## Klasör Yapısı
- `backend/`: FastAPI tabanlı API servisi.
- `frontend/`: React + Leaflet.js tabanlı dashboard.
- `iot_simulator/`: Sensör verilerini (HC-SR04) simüle eden istemci.
- `docs/`: Proje dökümanları ve raporlar.

## Kurulum
1. Gerekli Docker servislerini (TimescaleDB ve MQTT) başlatmak için:
   ```bash
   docker-compose up -d
   ```
2. Veritabanına `5432` portundan, MQTT broker'ına ise `1883` portundan erişebilirsiniz.

## Proje Ekibi (TideSense Ekibi)
- Enes Nebi Kaya (Backend, IoT)
- Nurullah Hançer (Proje Yönetimi)
- Abdallah M. K. Bakhit (Frontend)
- Hüseyin Deniz Kahya (Test/Analiz)
- Hasan Deniz (Kalite Güvence)
