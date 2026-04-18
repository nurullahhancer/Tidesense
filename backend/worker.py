import paho.mqtt.client as mqtt
import json, time
from datetime import datetime
from database import SessionLocal
from sqlalchemy import text

MQTT_BROKER = "localhost"
MQTT_TOPIC = "tidesense/sensor/readings"

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        db = SessionLocal()
        query = text("""
            INSERT INTO sensor_readings (time, sensor_id, water_level, temperature, humidity)
            VALUES (:time, :sensor_id, :water_level, :temperature, :humidity)
        """)
        reading_time = datetime.fromisoformat(data["timestamp"])
        db.execute(query, {
            "time": reading_time, "sensor_id": data["sensor_id"],
            "water_level": data["water_level"], "temperature": data.get("temperature"),
            "humidity": data.get("humidity")
        })
        db.commit()
        db.close()
        print(f"[{reading_time}] Kaydedildi: {data['water_level']} cm")
    except Exception as e:
        print(f"Hata: {e}")

def run_worker():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    
    while True:
        try:
            client.connect(MQTT_BROKER, 1883, 60)
            break
        except:
            time.sleep(5)

    client.subscribe(MQTT_TOPIC)
    print("MQTT Worker Çalışıyor...")
    client.loop_forever()

if __name__ == "__main__":
    run_worker()
