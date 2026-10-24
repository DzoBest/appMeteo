import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException

from appmeteo.clients.open_meteo_client import get_current_weather
from appmeteo.core.cities import DEFAULT_CITIES, City
from appmeteo.models.weather_measurement import WeatherMeasurement
from appmeteo.repositories.weather_repository import WeatherRepository
from appmeteo.schemas.weather import WeatherResponse

MAX_CONCURRENT_CITY_REQUESTS = 3
MAX_RATE_LIMIT_RETRIES = 3


async def get_weather(
    latitude: float,
    longitude: float,
    session: AsyncSession,
) -> WeatherResponse:
    """Récupère la météo unitaire pour des coordonnées et l'enregistre en base."""
    weather_repo = WeatherRepository(session=session)

    # 1. Appel du client externe
    raw_data = await get_current_weather(latitude, longitude)

    # 2. Validation schéma
    weather_data = WeatherResponse(**raw_data)

    # 3. Création du modèle
    measurement = WeatherMeasurement(
        latitude=weather_data.latitude,
        longitude=weather_data.longitude,
        timezone=weather_data.timezone,
        temperature_2m=weather_data.current.temperature_2m,
        relative_humidity_2m=weather_data.current.relative_humidity_2m,
        weather_code=weather_data.current.weather_code,
        raw_payload=raw_data,
    )

    # 4. Enregistrement via le Repository
    await weather_repo.create(measurement)

    return weather_data


async def _fetch_city_measurement(
    city: City,
    semaphore: asyncio.Semaphore,
) -> WeatherMeasurement | None:
    """Récupère les données météo d'une ville et construit le modèle de BDD."""
    async with semaphore:
        for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
            try:
                raw_data = await get_current_weather(city.latitude, city.longitude)
                weather_data = WeatherResponse(**raw_data)
                return WeatherMeasurement(
                    city_name=city.name,
                    latitude=city.latitude,
                    longitude=city.longitude,
                    timezone=weather_data.timezone,
                    temperature_2m=weather_data.current.temperature_2m,
                    relative_humidity_2m=weather_data.current.relative_humidity_2m,
                    weather_code=weather_data.current.weather_code,
                    raw_payload=raw_data,
                )
            except HTTPException as error:
                if error.status_code == 429 and attempt < MAX_RATE_LIMIT_RETRIES:
                    await asyncio.sleep(2**attempt)
                    continue
                print(f"Erreur lors de la collecte pour {city.name}: {error.detail}")
                return None
            except Exception as error:
                print(f"Erreur lors de la collecte pour {city.name}: {error}")
                return None


async def ingest_all_cities(
    session: AsyncSession,
    cities: list[City] = DEFAULT_CITIES,
) -> list[WeatherMeasurement]:
    """Ingère les données météo pour toutes les villes en parallèle et les stocke en base."""
    weather_repo = WeatherRepository(session=session)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CITY_REQUESTS)
    tasks = [_fetch_city_measurement(city, semaphore) for city in cities]
    results = await asyncio.gather(*tasks)

    # Filtrer les erreurs éventuelles
    measurements = [m for m in results if m is not None]

    # Sauvegarde par lot (Batch) en base de données
    if measurements:
        await weather_repo.create_many(measurements)

    return measurements