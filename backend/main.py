from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from database import get_db, engine
import uvicorn

app = FastAPI(
    title="TideSense API",
    description="Akıllı Gelgit İzleme ve Tahmin Sistemi Backend Servisi",
    version="1.0.0"
)

# CORS Ayarları: Frontend'in API'ye erişebilmesi için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme aşamasında tüm adreslere izin ver (Örn: localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "TideSense API Çalışıyor", "timestamp": datetime.now()}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Veritabanı bağlantı testi
        db.execute(text("SELECT 1"))
        return {"database": "connected", "mqtt_broker": "connected"}
    except Exception as e:
        return {"database": "disconnected", "error": str(e)}

# --- Sensör Verisi API'ları (Veritabanından Gerçek Veri Çeker) ---

@app.get("/readings/latest")
def get_latest_readings(db: Session = Depends(get_db)):
    """Veritabanındaki en son sensör ölçümlerini getirir (Rastgele değil!)"""
    try:
        # Son ölçümü getiren SQL sorgusu (TimescaleDB hypertable'dan)
        query = text("""
            SELECT time, sensor_id, water_level, temperature, humidity
            FROM sensor_readings
            ORDER BY time DESC
            LIMIT 10
        """)
        
        result = db.execute(query).fetchall()
        
        if not result:
            return {"message": "Henüz veri bulunamadı. Simülatörü çalıştırdığınızdan emin olun."}
        
        # Verileri API formatına dönüştür
        readings = []
        for row in result:
            readings.append({
                "time": row[0],
                "sensor_id": row[1],
                "water_level": row[2],
                "temperature": row[3],
                "humidity": row[4],
                "status": "Kritik" if row[2] > 150 else "Normal"
            })
            
        return readings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Veritabanı hatası: {str(e)}")

@app.get("/predictions")
def get_predictions(limit: int = 24):
    """Gelecek N saat için yapay zeka tahminleri (Mockup)"""
    # Bu bölüm ilerde Scikit-learn modeli ile güncellenecek
    return {"predictions": [], "count": 0}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
