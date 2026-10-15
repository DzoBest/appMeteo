import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

from appmeteo.clients.open_meteo_client import get_current_weather
from appmeteo.core.cities import DEFAULT_CITIES, City
from appmeteo.models.weather_measurement import WeatherMeasurement
from appmeteo.repositories.weather_repository import WeatherRepository
from appmeteo.schemas.weather import WeatherResponse


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


async def _fetch_city_measurement(city: City) -> WeatherMeasurement | None:
    """Récupère les données météo d'une ville et construit le modèle de BDD."""
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
    except Exception as e:
        print(f"Erreur lors de la collecte pour {city.name}: {e}")
        return None


async def ingest_all_cities(
    session: AsyncSession,
    cities: list[City] = DEFAULT_CITIES,
) -> list[WeatherMeasurement]:
    """Ingère les données météo pour toutes les villes en parallèle et les stocke en base."""
    weather_repo = WeatherRepository(session=session)

    # Collecte en parallèle grâce à asyncio.gather (ultra rapide !)
    tasks = [_fetch_city_measurement(city) for city in cities]
    results = await asyncio.gather(*tasks)

    # Filtrer les erreurs éventuelles
    measurements = [m for m in results if m is not None]

    # Sauvegarde par lot (Batch) en base de données
    if measurements:
        await weather_repo.create_many(measurements)

    return measurements