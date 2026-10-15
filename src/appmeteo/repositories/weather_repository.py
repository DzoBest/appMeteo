from collections.abc import Sequence
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from appmeteo.models.weather_measurement import WeatherMeasurement


class WeatherRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, measurement: WeatherMeasurement) -> WeatherMeasurement:
        """Enregistre une nouvelle mesure en base de données."""
        self.session.add(measurement)
        await self.session.commit()
        await self.session.refresh(measurement)
        return measurement

    async def get_latest_by_coordinates(
        self, latitude: float, longitude: float
    ) -> WeatherMeasurement | None:
        """Récupère la mesure la plus récente pour des coordonnées données."""
        statement = (
            select(WeatherMeasurement)
            .where(
                WeatherMeasurement.latitude == latitude,
                WeatherMeasurement.longitude == longitude,
            )
            .order_by(WeatherMeasurement.recorded_at.desc())
            .limit(1)
        )
        result = await self.session.exec(statement)
        return result.first()

    async def create_many(
        self, measurements: list[WeatherMeasurement]
    ) -> list[WeatherMeasurement]:
        """Enregistre un lot de plusieurs mesures en une seule transaction SQL."""
        self.session.add_all(measurements)
        await self.session.commit()
        for m in measurements:
            await self.session.refresh(m)
        return measurements

    async def get_history(
        self, latitude: float, longitude: float, limit: int = 100
    ) -> Sequence[WeatherMeasurement]:
        """Récupère l'historique des N dernières mesures pour des coordonnées données."""
        statement = (
            select(WeatherMeasurement)
            .where(
                WeatherMeasurement.latitude == latitude,
                WeatherMeasurement.longitude == longitude,
            )
            .order_by(WeatherMeasurement.recorded_at.desc())
            .limit(limit)
        )
        result = await self.session.exec(statement)
        return result.all()