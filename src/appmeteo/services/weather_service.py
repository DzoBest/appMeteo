from sqlmodel.ext.asyncio.session import AsyncSession
from appmeteo.clients.open_meteo_client import get_current_weather
from appmeteo.models.weather_measurement import WeatherMeasurement
from appmeteo.schemas.weather import WeatherResponse


async def get_weather(
    latitude: float,
    longitude: float,
    session: AsyncSession,
) -> WeatherResponse:
    # 1. Appel du client externe (renvoie un dictionnaire)
    raw_data = await get_current_weather(latitude, longitude)

    # 2. Validation avec Pydantic
    weather_data = WeatherResponse(**raw_data)

    # 3. Création de l'enregistrement en BDD en lisant `weather_data.current`
    measurement = WeatherMeasurement(
        latitude=weather_data.latitude,
        longitude=weather_data.longitude,
        timezone=weather_data.timezone,
        temperature_2m=weather_data.current.temperature_2m,
        relative_humidity_2m=weather_data.current.relative_humidity_2m,
        weather_code=weather_data.current.weather_code,
        raw_payload=raw_data,  # Couche Bronze
    )

    # 4. Sauvegarde dans PostgreSQL
    session.add(measurement)
    await session.commit()
    await session.refresh(measurement)

    # 5. Retour de la réponse
    return weather_data