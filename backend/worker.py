import paho.mqtt.client as mqtt
import json
from datetime import datetime
from database import SessionLocal
from sqlalchemy import text
import time

MQTT_BROKER = "localhost"
MQTT_TOPIC = "tidesense/sensor/readings"

def on_message(client, userdata, msg):
    try:
        # Gelen MQTT mesajını çöz
        data = json.loads(msg.payload.decode())
        db = SessionLocal()
        
        # SQL sorgusu ile veriyi TimescaleDB'ye kaydet
        query = text("""
            INSERT INTO sensor_readings (time, sensor_id, water_level, temperature, humidity)
            VALUES (:time, :sensor_id, :water_level, :temperature, :humidity)
        """)
        
        # Zaman bilgisini Python datetime objesine çevir
        reading_time = datetime.fromisoformat(data["timestamp"])
        
        db.execute(query, {
            "time": reading_time,
            "sensor_id": data["sensor_id"],
            "water_level": data["water_level"],
            "temperature": data.get("temperature"),
            "humidity": data.get("humidity")
        })
        
        db.commit()
        db.close()
        print(f"[{reading_time}] Veri kaydedildi: {data['sensor_id']} -> {data['water_level']} cm")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")

# MQTT İstemci Yapılandırması
def run_worker():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    
    # Broker'a bağlanana kadar bekle (Docker servisinin hazır olması için)
    connected = False
    while not connected:
        try:
            client.connect(MQTT_BROKER, 1883, 60)
            connected = True
        except:
            print("MQTT Broker'a bağlanılamıyor, 5 saniye sonra tekrar denenecek...")
            time.sleep(5)

    client.subscribe(MQTT_TOPIC)
    print(f"MQTT Worker Başlatıldı. '{MQTT_TOPIC}' kanalı dinleniyor...")
    client.loop_forever()

if __name__ == "__main__":
    run_worker()
