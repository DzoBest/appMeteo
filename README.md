# AppMeteo - Plateforme de Données Météorologiques

API REST moderne et performante construite avec **FastAPI**, **Pydantic** et **HTTPX**, permettant de récupérer les conditions météorologiques actuelles à partir du service Open-Meteo.

---

## 🌟 Fonctionnalités

- **Architecture en couches :** Séparation claire entre routes d'API, logique métier (services), clients externes et schémas de données.
- **I/O Asynchrone :** Utilisation de `httpx.AsyncClient` et endpoints asynchrones (`async def`) pour des performances et une scalabilité optimales.
- **Validation stricte & Typage :** Modèles Pydantic v2 assurant la validation des requêtes et réponses ainsi qu'une documentation Swagger/OpenAPI auto-générée.
- **Gestion centralisée de la configuration :** Prise en charge des variables d'environnement (`.env`) avec `pydantic-settings`.
- **Gestion des erreurs et Résilience :** Gestion propre des statuts HTTP, timeouts et erreurs de connectivité du service tiers.
- **Tests automatisés :** Suite de tests unitaires et d'intégration avec `pytest`.

---

## 🚀 Installation & Démarrage

### Prérequis

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) (recommandé) ou `pip`

### 1. Cloner et installer les dépendances

Avec `uv` :
```bash
uv sync
```

### 2. Configuration (Optionnel)

Vous pouvez créer un fichier `.env` à la racine pour surcharger les valeurs par défaut :
```env
APP_NAME="Weather Data Platform"
OPEN_METEO_URL="https://api.open-meteo.com/v1/forecast"
DEFAULT_TIMEZONE="Europe/Paris"
REQUEST_TIMEOUT_SECONDS=10.0
```

### 3. Lancer l'application

```bash
uv run fastapi dev src/appmeteo/main.py
```

L'application sera accessible sur : `http://127.0.0.1:8000`

---

## 📚 Documentation API & Endpoints

Une fois le serveur démarré, la documentation interactive est disponible sur :
- **Swagger UI :** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc :** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Endpoints principaux

- `GET /health` : Vérification de l'état de l'API.
- `GET /weather?lat=49.4432&lon=1.0993` : Récupère la météo actuelle pour des coordonnées données.

---

## 🧪 Lancer les tests

```bash
uv run pytest
```
