from fastapi import FastAPI
from appmeteo.api.routes.weather import router as weather_router

app = FastAPI(
    title = "weather data plateform",
    version  = "0.1.0"
    )

app.include_router(weather_router)