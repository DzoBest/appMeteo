from pydantic import BaseModel, Field


class WeatherData(BaseModel):
    time: str = Field(..., description="Timestamp of the weather reading")
    interval: int = Field(..., description="Interval in seconds")
    temperature_2m: float = Field(..., description="Air temperature at 2 meters above ground (°C)")
    relative_humidity_2m: int = Field(..., description="Relative humidity at 2 meters above ground (%)")
    weather_code: int = Field(..., description="WMO Weather interpretation code")


class WeatherResponse(BaseModel):
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    timezone: str = Field(..., description="Timezone used for timestamps")
    current: WeatherData = Field(..., description="Current weather conditions")
