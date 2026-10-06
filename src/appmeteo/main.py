import requests
from fastapi import FastAPI

app = FastAPI()

URL = "https://api.open-meteo.com/v1/forecast"


@app.get("/meteo")
def meteo(lat: float = 49.4432, lon: float = 1.0993):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
        "timezone": "Europe/Paris",
    }
    response = requests.get(URL, params=params)
    response.raise_for_status()
    return response.json()["current"]