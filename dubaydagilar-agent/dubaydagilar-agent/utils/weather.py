"""Dubay ob-havosini OpenWeatherMap orqali oladi."""

import logging
import requests
from config import OPENWEATHER_API_KEY, DUBAI_LAT, DUBAI_LON

logger = logging.getLogger("weather")

API_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_dubai_weather():
    """
    Natija: {'temp':, 'feels_like':, 'description':, 'humidity':, 'wind_speed':}
    Xato bo'lsa None qaytaradi.
    """
    params = {
        "lat": DUBAI_LAT,
        "lon": DUBAI_LON,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "en",
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return {
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }
    except (requests.RequestException, KeyError, IndexError) as e:
        logger.error("Ob-havo olishda xato: %s", e)
        return None
