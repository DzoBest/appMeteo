import httpx
from fastapi import HTTPException, status

from appmeteo.core.config import settings


async def get_current_weather(latitude: float, longitude: float) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "weather_code",
        ],
        "timezone": settings.default_timezone,
    }

    try:
        async  with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(settings.open_meteo_url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Open-Meteo API returned an error: {exc.response.text}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to connect to Open-Meteo service: {str(exc)}",
        ) from exc