import paho.mqtt.client as mqtt
import time
import json
import random
import math
from datetime import datetime

# --- Ayarlar (Configuration) ---
MQTT_BROKER = "localhost" # Docker-compose üzerinden yerel port (1883)
MQTT_PORT = 1883
MQTT_TOPIC = "tidesense/sensor/readings"
SENSOR_ID = "Tide-01"

# --- Bağlantı Ayarları ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def connect_mqtt():
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Connected to MQTT Broker: {MQTT_BROKER}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False
    return True

# --- Veri Simülasyonu ---
def generate_tide_data(tick):
    """
    Basit bir sinüs dalgası ile gelgit seviyesini taklit eder.
    Gerçek gelgit yaklaşık 12.4 saatlik bir periyoda sahiptir.
    """
    amplitude = 150  # cm (Gelgit aralığı)
    offset = 200     # cm (Ortalama su seviyesi)
    frequency = 0.05 # Hız
    
    # Su seviyesini hesapla (Sinüs dalgası + Küçük rastgele gürültü)
    water_level = offset + (amplitude * math.sin(tick * frequency)) + random.uniform(-2, 2)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "sensor_id": SENSOR_ID,
        "water_level": round(water_level, 2),
        "temperature": round(random.uniform(15.0, 22.0), 1),
        "humidity": round(random.uniform(60.0, 85.0), 1),
        "unit": "cm"
    }

# --- Ana Döngü ---
def run():
    if not connect_mqtt():
        return

    tick = 0
    print("Simülatör başlatıldı. Veriler gönderiliyor...")
    
    try:
        while True:
            data = generate_tide_data(tick)
            payload = json.dumps(data)
            
            # Veriyi MQTT broker'a yayınla
            client.publish(MQTT_TOPIC, payload)
            print(f"Published: {payload}")
            
            tick += 1
            time.sleep(5) # 5 saniyede bir veri gönder
            
    except KeyboardInterrupt:
        print("Simülatör durduruldu.")
        client.disconnect()

if __name__ == "__main__":
    run()
