import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from appmeteo.main import app

client = TestClient(app)

MOCK_OPEN_METEO_RESPONSE = {
    "latitude": 49.44,
    "longitude": 1.1,
    "generationtime_ms": 0.05,
    "utc_offset_seconds": 7200,
    "timezone": "Europe/Paris",
    "timezone_abbreviation": "CEST",
    "elevation": 10.0,
    "current": {
        "time": "2026-10-08T18:00",
        "interval": 900,
        "temperature_2m": 15.2,
        "relative_humidity_2m": 72,
        "weather_code": 1,
    },
}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_weather_endpoint_success():
    with patch(
        "appmeteo.clients.open_meteo_client.httpx.AsyncClient.get",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: MOCK_OPEN_METEO_RESPONSE
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response

        response = client.get("/weather?lat=49.4432&lon=1.0993")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["latitude"] == 49.44
        assert json_data["longitude"] == 1.1
        assert json_data["timezone"] == "Europe/Paris"
        assert json_data["current"]["temperature_2m"] == 15.2
        assert json_data["current"]["relative_humidity_2m"] == 72
        assert json_data["current"]["weather_code"] == 1


def test_weather_endpoint_invalid_coordinates():
    # Latitude > 90
    response = client.get("/weather?lat=95.0&lon=1.0")
    assert response.status_code == 422

    # Longitude < -180
    response = client.get("/weather?lat=45.0&lon=-190.0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_weather_endpoint_upstream_error():
    import httpx

    with patch(
        "appmeteo.clients.open_meteo_client.httpx.AsyncClient.get",
        side_effect=httpx.ConnectError("Connection refused"),
    ):
        response = client.get("/weather?lat=49.4432&lon=1.0993")
        assert response.status_code == 503
        assert "Unable to connect" in response.json()["detail"]
