"""OpenWeatherMap current-weather integration."""

from typing import Any

import requests


BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherServiceError(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def get_current_weather(city: str, api_key: str) -> dict[str, Any]:
    """Fetch and normalize the current weather for a city in metric units."""
    if not api_key:
        raise WeatherServiceError(
            "Weather service is not configured. Add OPENWEATHER_API_KEY to .env.", 503
        )

    try:
        response = requests.get(
            BASE_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
    except requests.RequestException:
        raise WeatherServiceError("Unable to reach the weather service. Please try again.")

    if response.status_code == 404:
        raise WeatherServiceError("City not found. Check the spelling and try again.", 404)
    if response.status_code in (401, 403):
        raise WeatherServiceError("Weather service credentials are invalid or unavailable.", 503)
    if response.status_code == 429:
        raise WeatherServiceError("Weather service rate limit reached. Please try again shortly.", 429)
    if not response.ok:
        raise WeatherServiceError("Weather service is temporarily unavailable. Please try again.")

    try:
        data = response.json()
        weather = data["weather"][0]
        main = data["main"]
        wind = data.get("wind", {})
        sys = data.get("sys", {})
        return {
            "city": data["name"],
            "country": sys.get("country", ""),
            "temperature": round(main["temp"]),
            "feels_like": round(main["feels_like"]),
            "humidity": main["humidity"],
            "wind_speed": round(wind.get("speed", 0) * 3.6, 1),
            "condition": weather["main"],
            "description": weather["description"].capitalize(),
            "icon": weather.get("icon", "01d"),
        }
    except (KeyError, IndexError, TypeError, ValueError):
        raise WeatherServiceError("Weather service returned an unexpected response.")
