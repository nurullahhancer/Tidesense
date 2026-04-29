import json
import math
import os
import random
import time
import urllib.request
from datetime import UTC, datetime

import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "tidesense")

STATIONS = [
    {"code": "ISK_LIMAN", "offset": 0.2, "lat": 36.587, "lon": 36.166},
    {"code": "IZM_ALSANCAK", "offset": 0.7, "lat": 38.438, "lon": 27.144},
    {"code": "IST_BOGAZ", "offset": 1.4, "lat": 41.026, "lon": 29.015},
    {"code": "TRB_LIMAN", "offset": 1.9, "lat": 41.008, "lon": 39.728},
]

weather_cache = {}
last_weather_fetch = 0

def fetch_real_weather():
    global last_weather_fetch, weather_cache
    now = time.time()
    if now - last_weather_fetch < 900 and weather_cache:
        return
        
    for station in STATIONS:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={station['lat']}&longitude={station['lon']}&current=temperature_2m,surface_pressure"
            req = urllib.request.Request(url, headers={'User-Agent': 'TideSense Simulator'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                current = data.get("current", {})
                temp = current.get("temperature_2m")
                pres = current.get("surface_pressure")
                if temp is not None and pres is not None:
                    weather_cache[station['code']] = {"temp": temp, "pres": pres}
        except Exception as e:
            print(f"Weather fetch failed for {station['code']}: {e}")
            
    last_weather_fetch = now

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


def connect_mqtt() -> bool:
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"MQTT connection failed: {exc}")
        return False


def generate_payload(station_code: str, offset: float, tick: int) -> dict:
    base = 104 + math.sin((tick / 9) + offset) * 24
    
    real_data = weather_cache.get(station_code)
    if real_data:
        pressure = real_data["pres"] + random.uniform(-0.2, 0.2)
        temperature = real_data["temp"] + random.uniform(-0.1, 0.1)
    else:
        pressure = 1010 + math.cos((tick / 12) + offset) * 7 + random.uniform(-0.6, 0.6)
        temperature = 18 + math.sin((tick / 16) + offset) * 5 + random.uniform(-0.5, 0.5)

    return {
        "station_code": station_code,
        "recorded_at": datetime.now(UTC).isoformat(),
        "water_level_cm": round(base + random.uniform(-1.8, 1.8), 2),
        "air_pressure_hpa": round(pressure, 2),
        "temperature_c": round(temperature, 2),
    }


def run() -> None:
    if not connect_mqtt():
        return

    tick = 0
    print("TideSense station simulator started.")
    while True:
        fetch_real_weather()
        for station in STATIONS:
            topic = f"{MQTT_TOPIC_PREFIX}/stations/{station['code']}/telemetry"
            payload = generate_payload(station["code"], station["offset"], tick)
            client.publish(topic, json.dumps(payload))
            print(f"Published {station['code']} -> {payload['water_level_cm']} cm")
        tick += 1
        time.sleep(8)


if __name__ == "__main__":
    run()
