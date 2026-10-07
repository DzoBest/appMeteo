from appmeteo.clients.open_meteo_client import get_current_weather


def get_weather(latitude: float, longitude: float) -> dict:
    return get_current_weather(latitude, longitude)