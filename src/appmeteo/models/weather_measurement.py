from datetime import datetime, timezone
from typing import Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB


class WeatherMeasurement(SQLModel, table=True):
    __tablename__ = "weather_measurements"

    id: int | None = Field(default=None, primary_key=True)
    city_name: str | None = Field(default=None, index=True)
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
    latitude: float = Field(index=True)
    longitude: float = Field(index=True)
    timezone: str | None = None
    temperature_2m: float
    relative_humidity_2m: int | None = None
    weather_code: int | None = None

    # Couche Bronze : stockage du payload JSON complet
    raw_payload: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))