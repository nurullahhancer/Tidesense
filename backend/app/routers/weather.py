from datetime import UTC, datetime
from typing import Any

import asyncio
import random

import httpx
from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter(prefix="/api/v1", tags=["weather"])

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
REQUEST_TIMEOUT_SECONDS = 8.0

# Bellek içi önbellek
_weather_cache: dict[str, tuple[datetime, dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 1800  # 30 dakika

# Open-Meteo burst limitlerini aşmamak için aynı anda en fazla 10 isteğe izin ver
_api_semaphore = asyncio.Semaphore(10)

# Global HTTPX Client
_http_client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS)


WMO_WEATHER_DESCRIPTIONS: dict[int, str] = {
    code: "Hava durumu" for code in range(100)
}
WMO_WEATHER_DESCRIPTIONS.update(
    {
        0: "Açık",
        1: "Çoğunlukla açık",
        2: "Parçalı bulutlu",
        3: "Kapalı",
        45: "Sisli",
        48: "Kırağılaşan sis",
        51: "Hafif çisenti",
        53: "Orta şiddette çisenti",
        55: "Yoğun çisenti",
        56: "Hafif dondurucu çisenti",
        57: "Yoğun dondurucu çisenti",
        61: "Hafif yağmurlu",
        63: "Orta şiddette yağmurlu",
        65: "Şiddetli yağmurlu",
        66: "Hafif dondurucu yağmur",
        67: "Şiddetli dondurucu yağmur",
        71: "Hafif kar yağışı",
        73: "Orta şiddette kar yağışı",
        75: "Şiddetli kar yağışı",
        77: "Kar taneleri",
        80: "Hafif sağanak yağış",
        81: "Orta şiddette sağanak yağış",
        82: "Şiddetli sağanak yağış",
        85: "Hafif kar sağanağı",
        86: "Şiddetli kar sağanağı",
        95: "Gök gürültülü fırtına",
        96: "Hafif dolu yağışlı fırtına",
        99: "Şiddetli dolu yağışlı fırtına",
    }
)


def _current(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("current") or {}


def _get_any(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload:
            return payload[key]
    return None


async def _fetch_forecast(
    client: httpx.AsyncClient,
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weathercode,windspeed_10m,winddirection_10m",
    }
    modern_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code,wind_speed_10m,wind_direction_10m",
    }

    response = await client.get(FORECAST_URL, params=params)
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        response = await client.get(FORECAST_URL, params=modern_params)
    response.raise_for_status()
    return response.json()


async def _fetch_marine(
    client: httpx.AsyncClient,
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    response = await client.get(
        MARINE_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "wave_height,wave_period,wave_direction",
        },
    )
    response.raise_for_status()
    return response.json()


def _get_mock_weather(lat: float, lon: float, now: datetime) -> dict[str, Any]:
    """API başarısız olduğunda dönülecek tahmini (mock) veriler."""
    # Koordinat ve saate göre sabit seed oluşturarak tutarlılık sağla
    seed = int(abs(lat) * 100 + abs(lon) * 100) + now.hour
    random.seed(seed)
    
    # Mevsime/saate göre çok absürt olmayacak değerler
    temp = 15 + random.random() * 10 # 15-25 arası
    wind = 5 + random.random() * 12 # 5-17 arası
    pressure = 1005 + random.random() * 15 # 1005-1020 arası
    code = random.choice([0, 1, 2, 3])
    
    weather_desc = WMO_WEATHER_DESCRIPTIONS.get(code, "Açık")
    return {
        "temperature_c": round(temp, 1),
        "air_pressure_hpa": round(pressure, 1),
        "weather_code": code,
        "weather_description": weather_desc,
        "wind_speed_kmh": round(wind, 1),
        "wind_direction_deg": random.randint(0, 360),
        "wave_height_m": 0.4,
        "wave_period_s": 4.5,
        "wave_direction_deg": random.randint(0, 360),
        "fetched_at": now.isoformat().replace("+00:00", "Z"),
        "is_mock": True
    }


@router.get("/weather")
async def get_weather(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
) -> dict[str, Any]:
    cache_key = f"{lat:.2f}_{lon:.2f}"
    now = datetime.now(UTC)
    
    if cache_key in _weather_cache:
        cached_at, cached_data = _weather_cache[cache_key]
        if (now - cached_at).total_seconds() < CACHE_TTL_SECONDS:
            return cached_data

    forecast_payload = {}
    marine_payload = {}
    
    try:
        async with _api_semaphore:
            # Hava tahmini (Kısa timeout ile)
            try:
                resp = await _http_client.get(
                    FORECAST_URL,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl",
                    },
                    timeout=3.0 
                )
                if resp.status_code == 200:
                    forecast_payload = resp.json()
                else:
                    # Rate limit veya hata varsa hemen mock'a düş
                    raise Exception("API Limit")
            except Exception:
                if cache_key in _weather_cache: return _weather_cache[cache_key][1]
                return _get_mock_weather(lat, lon, now)

            # Deniz verisi (Opsiyonel)
            try:
                resp_m = await _http_client.get(
                    MARINE_URL,
                    params={"latitude": lat, "longitude": lon, "current": "wave_height"},
                    timeout=2.0
                )
                if resp_m.status_code == 200:
                    marine_payload = resp_m.json()
            except Exception:
                pass
                
    except Exception:
        if cache_key in _weather_cache: return _weather_cache[cache_key][1]
        return _get_mock_weather(lat, lon, now)

    forecast = _current(forecast_payload)
    marine = _current(marine_payload)
    
    _w_code = _get_any(forecast, "weather_code", "weathercode")
    weather_code_int = int(_w_code) if _w_code is not None else 0
    weather_description = WMO_WEATHER_DESCRIPTIONS.get(weather_code_int, "Hava durumu")
    
    # Basınç ve sıcaklık için tutarlı rastgelelik (eğer API'den gelmezse veya ekstra varyasyon istenirse)
    # Burada kullanıcı "rastgele atanacak ama tutarlı olacak" dediği için 
    # API değerine çok küçük bir gürültü ekleyebiliriz veya API yoksa mock kullanabiliriz.
    # Şimdilik API değerini önceliklendirip yoksa rastgele üretiyoruz.
    
    seed = int(abs(lat) * 100 + abs(lon) * 100) + now.hour
    random.seed(seed)
    
    api_temp = _get_any(forecast, "temperature_2m")
    api_pressure = _get_any(forecast, "pressure_msl")
    
    temperature = api_temp if api_temp is not None else (15 + random.random() * 10)
    pressure = api_pressure if api_pressure is not None else (1005 + random.random() * 15)
    
    result = {
        "temperature_c": round(temperature, 1),
        "air_pressure_hpa": round(pressure, 1),
        "weather_code": weather_code_int,
        "weather_description": weather_description,
        "wind_speed_kmh": _get_any(forecast, "wind_speed_10m", "windspeed_10m") or 10.0,
        "wind_direction_deg": _get_any(forecast, "wind_direction_10m", "winddirection_10m") or 0,
        "wave_height_m": _get_any(marine, "wave_height") or 0.3,
        "wave_period_s": 4.0,
        "wave_direction_deg": 0,
        "fetched_at": now.isoformat().replace("+00:00", "Z"),
    }
    
    _weather_cache[cache_key] = (now, result)
    return result
