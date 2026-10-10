from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI

from appmeteo.api.routes import weather
from appmeteo.core.config import settings
from appmeteo.core.db import init_db
import appmeteo.models  # Permet à SQLModel d'enregistrer les modèles avant init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Code exécuté AU DÉMARRAGE de FastAPI
    await init_db()
    yield
    # Code exécuté À L'ARRÊT de FastAPI (si besoin de fermer des connexions)


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(weather.router)


@app.get("/", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}