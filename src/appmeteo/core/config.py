from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Weather Data Platform"
    app_version: str = "0.1.0"
    open_meteo_url: str = "https://api.open-meteo.com/v1/forecast"
    default_timezone: str = "Europe/Paris"
    request_timeout_seconds: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
