import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def get_current_weather(latitude: float, longitude: float) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current":[
            "temperature_2m",
            "relative_humidity_2m",
            "weather_code",
        ],
        "timezone": "Europe/Paris",
    }

    response = requests.get(OPEN_METEO_URL, params = params, timeout = 10)

    response.raise_for_status()
    return response.json()["current"]