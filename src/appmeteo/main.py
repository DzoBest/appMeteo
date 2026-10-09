from fastapi import FastAPI
from appmeteo.api.routes.weather import router as weather_router
from appmeteo.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for fetching weather data from Open-Meteo",
)

app.include_router(weather_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}