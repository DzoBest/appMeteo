from pydantic import BaseModel

class City(BaseModel):
    name: str
    latitude: float
    longitude: float

# Référentiel des villes à surveiller pour notre plateforme data
DEFAULT_CITIES: list[City] = [
    City(name="Paris", latitude=48.8566, longitude=2.3522),
    City(name="Marseille", latitude=43.2965, longitude=5.3698),
    City(name="Lyon", latitude=45.7640, longitude=4.8357),
    City(name="Toulouse", latitude=43.6047, longitude=1.4442),
    City(name="Nice", latitude=43.7102, longitude=7.2620),
    City(name="Nantes", latitude=47.2184, longitude=-1.5536),
    City(name="Strasbourg", latitude=48.5734, longitude=7.7521),
    City(name="Montpellier", latitude=43.6108, longitude=3.8767),
    City(name="Bordeaux", latitude=44.8378, longitude=-0.5792),
    City(name="Lille", latitude=50.6292, longitude=3.0573),
    City(name="Rouen", latitude=49.4432, longitude=1.0993),
]