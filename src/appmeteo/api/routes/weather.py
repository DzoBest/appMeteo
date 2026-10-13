from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from appmeteo.core.db import get_session
from appmeteo.schemas.weather import WeatherResponse
from appmeteo.services.weather_service import get_weather

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get(
    "",
    response_model=WeatherResponse,
    summary="Get current weather",
    description="Retrieve current meteorological conditions for given geographic coordinates and save them.",
)
async def get_current_weather_endpoint(
    lat: float = Query(
        49.4432,
        ge=-90.0,
        le=90.0,
        description="Latitude of the location (-90 to 90)",
        examples=[49.4432],
    ),
    lon: float = Query(
        1.0993,
        ge=-180.0,
        le=180.0,
        description="Longitude of the location (-180 to 180)",
        examples=[1.0993],
    ),
    session: AsyncSession = Depends(get_session),
) -> WeatherResponse:
    return await get_weather(latitude=lat, longitude=lon, session=session)