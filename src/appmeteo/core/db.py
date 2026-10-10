from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from appmeteo.core.config import settings

# Création du moteur asynchrone
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Fonction pour créer toutes les tables déclarées SQLModel
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Génération de session pour l'injection de dépendances dans FastApi
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
