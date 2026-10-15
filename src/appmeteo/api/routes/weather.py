from collections.abc import Sequence
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from appmeteo.core.db import get_session
from appmeteo.models.weather_measurement import WeatherMeasurement
from appmeteo.repositories.weather_repository import WeatherRepository
from appmeteo.schemas.weather import WeatherResponse
from appmeteo.services.weather_service import get_weather, ingest_all_cities

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


@router.post(
    "/ingest",
    status_code=status.HTTP_201_CREATED,
    summary="Ingest weather data for all configured cities",
    description="Fetch current weather for all default cities in parallel and store them in PostgreSQL.",
)
async def ingest_weather_data_endpoint(
    session: AsyncSession = Depends(get_session),
) -> dict[str, str | int]:
    measurements = await ingest_all_cities(session=session)
    return {
        "status": "success",
        "message": f"Successfully ingested weather data for {len(measurements)} cities.",
        "count": len(measurements),
    }


@router.get(
    "/history",
    response_model=list[WeatherMeasurement],
    summary="Get weather history for a location",
    description="Retrieve historical measurements recorded in the database for given coordinates.",
)
async def get_weather_history_endpoint(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude"),
    limit: int = Query(20, ge=1, le=500, description="Max number of records"),
    session: AsyncSession = Depends(get_session),
) -> Sequence[WeatherMeasurement]:
    weather_repo = WeatherRepository(session=session)
    return await weather_repo.get_history(latitude=lat, longitude=lon, limit=limit)