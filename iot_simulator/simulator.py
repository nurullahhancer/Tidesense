import paho.mqtt.client as mqtt
import time, json, random, math
from datetime import datetime

MQTT_BROKER = "localhost"
MQTT_TOPIC = "tidesense/sensor/readings"
SENSOR_ID = "Tide-01"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def generate_tide_data(tick):
    water_level = 200 + (150 * math.sin(tick * 0.05)) + random.uniform(-2, 2)
    return {
        "timestamp": datetime.now().isoformat(),
        "sensor_id": SENSOR_ID,
        "water_level": round(water_level, 2),
        "temperature": round(random.uniform(15.0, 22.0), 1),
        "humidity": round(random.uniform(60.0, 85.0), 1)
    }

if __name__ == "__main__":
    try:
        client.connect(MQTT_BROKER, 1883, 60)
        print("Simülatör başlatıldı...")
        tick = 0
        while True:
            data = generate_tide_data(tick)
            client.publish(MQTT_TOPIC, json.dumps(data))
            print(f"Gönderildi: {data['water_level']} cm")
            tick += 1
            time.sleep(5)
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
