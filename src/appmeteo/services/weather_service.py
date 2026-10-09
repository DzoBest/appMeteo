from appmeteo.clients.open_meteo_client import get_current_weather
from appmeteo.schemas.weather import WeatherResponse


async def get_weather(latitude: float, longitude: float) -> WeatherResponse:
    data = await get_current_weather(latitude=latitude, longitude=longitude)
    return WeatherResponse.model_validate(data)