from fastapi import APIRouter

from appmeteo.services.weather_service import get_weather

router = APIRouter()

@router.get("/meteo")
def meteo (
            lat: float = 49.4432,
            lon: float = 1.0993
        ):
   return get_weather(lat, lon)