from datetime import datetime
from typing import Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB


class WeatherMeasurement(SQLModel, table=True):
    __tablename__ = "weather_measurements"

    id: int | None = Field(default=None, primary_key=True)
    recorded_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    latitude: float = Field(index=True)
    longitude: float = Field(index=True)
    temperature: float
    humidity: float | None = None
    weather_code: int | None = None
    wind_speed: float | None = None

    # Couche Bronze : stockage du JSON brut complet envoyé par l'API
    raw_payload: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))