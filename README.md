# AppMeteo - Plateforme de Données Météorologiques

API REST et pipeline d'ingestion de données météorologiques construits avec **FastAPI**, **SQLModel**, **PostgreSQL**, **Docker**, et **Open-Meteo**.

---

## 🌟 Fonctionnalités

- **Clean Architecture en couches :** Séparation stricte entre les Routes (`api/routes`), la logique métier (`services`), l'accès aux données (`repositories`), les clients externes (`clients`), les modèles BDD (`models`) et les contrats d'échange (`schemas`).
- **Base de Données & ORM Asynchrone :** Persistance dans **PostgreSQL 16** via **SQLModel** et le driver asynchrone ultra-performant **asyncpg**.
- **Architecture Data Médaillon :**
  - **Couche Bronze :** Stockage du payload JSON brut complet (`raw_payload` en format `JSONB`) pour une traçabilité totale et le rejeu de données.
  - **Couche Silver :** Données structurées, typées et indexées (`temperature_2m`, `city_name`, `recorded_at`, etc.).
- **Ingestion par lots (Batch) Parallélisée :** Collecte simultanée des relevés de plusieurs villes de référence grâce à `asyncio.gather`.
- **Conteneurisation complète avec Docker Compose :** Déploiement et exécution d'un seul bloc (API FastAPI + BDD PostgreSQL avec volume persistant).
- **Validation stricte & Typage :** Modèles Pydantic v2 assurant la validation des requêtes et réponses avec documentation Swagger/OpenAPI interactive.

---

## 🚀 Installation & Démarrage

### Option 1 : Avec Docker Compose (Recommandé)

Prérequis : [Docker Desktop](https://www.docker.com/) installé et lancé.

1. **Lancer l'application et la base de données :**
   ```bash
   docker compose up -d --build
   ```

2. **Vérifier l'état des conteneurs :**
   ```bash
   docker compose ps
   ```

3. **Arrêter les services :**
   ```bash
   docker compose down
   ```
   *(Pour réinitialiser complètement la base de données et les volumes : `docker compose down -v`)*

---

### Option 2 : Développement Local (avec Python & uv)

Prérequis : Python >= 3.12, [uv](https://docs.astral.sh/uv/) et PostgreSQL lancé (ex. via `docker compose up -d db`).

1. **Installer les dépendances :**
   ```bash
   uv sync
   ```

2. **Lancer le serveur de développement :**
   ```bash
   uv run fastapi dev
   ```

L'application sera accessible sur : `http://127.0.0.1:8000`

---

## 📚 Endpoints & Documentation API

Documentation interactive disponible sur :
- **Swagger UI :** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc :** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Endpoints disponibles :

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health Check et statut de l'application |
| `GET` | `/weather` | Récupère la météo actuelle pour des coordonnées GPS (`lat`, `lon`) et l'enregistre en base |
| `POST` | `/weather/ingest` | Déclenche l'ingestion par lots en parallèle pour toutes les villes configurées |
| `GET` | `/weather/history` | Récupère l'historique des relevés enregistrés pour des coordonnées GPS données |

---

## 🔍 Commandes Utiles pour la Base de Données

Inspecter directement les données dans PostgreSQL :

```powershell
# Afficher les 15 derniers relevés ingérés
docker exec -it appmeteo_db psql -U appmeteo -d appmeteo -c "SELECT id, city_name, temperature_2m, relative_humidity_2m, recorded_at FROM weather_measurements ORDER BY id DESC LIMIT 15;"

# Afficher la structure de la table
docker exec -it appmeteo_db psql -U appmeteo -d appmeteo -c "\d weather_measurements"
```

---

## 🧪 Lancer les tests

```bash
uv run pytest
```
