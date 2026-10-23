# AppMeteo - Plateforme de données météorologiques

AppMeteo collecte les données météo d'Open-Meteo, les stocke dans PostgreSQL,
puis les transforme avec dbt. L'application expose une API FastAPI et un DAG
Airflow orchestre l'ingestion périodique des villes configurées.

## Architecture

```text
Open-Meteo
    │
    ▼
FastAPI ──► PostgreSQL (public.weather_measurements / couche Bronze)
    ▲
    │ POST /weather/ingest
    │
Airflow (DAG horaire)
    │
    ▼
dbt ──► silver.silver_weather ──► gold.mart_daily_weather_summary
```

Le dépôt contient les principaux composants suivants :

```text
src/appmeteo/                 API, services, repositories et modèles SQLModel
dags/weather_ingestion_dag.py DAG Airflow d'ingestion multi-villes
transform_meteo/              Projet dbt et modèle Silver
tests/                        Tests de l'API
docker-compose.yml            PostgreSQL, API et services Airflow
```

### Fonctionnalités

- API REST FastAPI documentée avec Swagger et ReDoc.
- Collecte unitaire pour des coordonnées GPS et enregistrement automatique en
  base.
- Ingestion batch parallèle des 11 villes du référentiel par défaut :
  Paris, Marseille, Lyon, Toulouse, Nice, Nantes, Strasbourg, Montpellier,
  Bordeaux, Lille et Rouen.
- Stockage des mesures dans PostgreSQL avec :
  - les colonnes structurées (`city_name`, `temperature_2m`,
    `relative_humidity_2m`, `weather_code`, `recorded_at`, etc.) ;
  - le payload Open-Meteo complet dans `raw_payload` au format JSONB.
- DAG Airflow `weather_batch_ingestion_dag`, exécuté toutes les heures, avec
  deux tentatives de reprise et un délai de cinq minutes entre les tentatives.
- Modèle dbt `silver_weather` matérialisé en incrémental :
  - lit `public.weather_measurements` ;
  - conserve les mesures dont la température et l'humidité sont renseignées ;
  - ne traite, après le premier lancement, que les mesures plus récentes que
    le maximum déjà présent dans la table cible ;
  - vérifie les colonnes `city_name`, `temperature_2m` et `recorded_at` avec
    des tests `not_null`.
- Modèle dbt Gold `mart_daily_weather_summary`, matérialisé en table dans le
  schéma PostgreSQL `gold`, avec les agrégats journaliers par ville
  (température moyenne, minimale, maximale, humidité moyenne et nombre de
  mesures).

## Prérequis

- [Docker Desktop](https://www.docker.com/) et Docker Compose ;
- pour le développement local : Python 3.12 ou supérieur et
  [uv](https://docs.astral.sh/uv/) ;
- pour exécuter dbt hors conteneur : dbt Core avec l'adaptateur PostgreSQL et
  un profil `transform_meteo` configuré dans `~/.dbt/profiles.yml`.

## Démarrage avec Docker Compose

Le démarrage recommandé lance PostgreSQL, l'API FastAPI et Airflow avec une
image Airflow locale contenant `dbt-core` et `dbt-postgres` :

```bash
copy transform_meteo\profiles.yml.example transform_meteo\profiles.yml
docker compose up -d --build
```

Le fichier `transform_meteo/profiles.yml` est ignoré par Git. Il lit les
paramètres de connexion dans les variables `DBT_DB_HOST`, `DBT_DB_PORT`,
`DBT_DB_USER`, `DBT_DB_PASSWORD`, `DBT_DB_NAME`, `DBT_DB_SCHEMA` et
`DBT_THREADS`, fournies aux conteneurs Airflow par `docker-compose.yml`.
Adaptez ces variables si les identifiants PostgreSQL changent.

Vérifier l'état des services :

```bash
docker compose ps
docker compose logs -f api
```

Les interfaces sont disponibles aux adresses suivantes :

| Service | URL |
| --- | --- |
| API | <http://127.0.0.1:8000> |
| Swagger UI | <http://127.0.0.1:8000/docs> |
| ReDoc | <http://127.0.0.1:8000/redoc> |
| Airflow | <http://127.0.0.1:8080> |

Le compte Airflow de développement est initialisé par `airflow-init`. Les
identifiants définis dans `docker-compose.yml` doivent être remplacés avant
toute utilisation dans un environnement partagé ou de production.

Arrêter les services sans supprimer les données :

```bash
docker compose down
```

Réinitialiser également le volume PostgreSQL :

```bash
docker compose down -v
```

## API

### Consulter la météo actuelle

`GET /weather` accepte une latitude et une longitude. Les valeurs par défaut
sont `49.4432` et `1.0993`.

```bash
curl "http://127.0.0.1:8000/weather?lat=48.8566&lon=2.3522"
```

La réponse est enregistrée dans `public.weather_measurements` et contient les
conditions actuelles renvoyées par Open-Meteo.

### Déclencher une ingestion batch

```bash
curl -X POST http://127.0.0.1:8000/weather/ingest
```

La réponse indique le nombre de villes effectivement ingérées. Les erreurs de
collecte d'une ville sont isolées des autres collectes.

Le DAG Airflow appelle ce même endpoint via le réseau Docker :

```text
http://api:8000/weather/ingest
```

### Consulter l'historique

```bash
curl "http://127.0.0.1:8000/weather/history?lat=48.8566&lon=2.3522&limit=20"
```

`limit` vaut 20 par défaut et accepte une valeur comprise entre 1 et 500.
L'historique est renvoyé du relevé le plus récent au plus ancien.

### Vérifier l'état de l'application

```bash
curl http://127.0.0.1:8000/
```

## Développement local

Installer les dépendances :

```bash
uv sync
```

Démarrer uniquement PostgreSQL avec Compose :

```bash
docker compose up -d db
```

Puis lancer l'API :

```bash
uv run fastapi dev
```

La variable `DATABASE_URL` peut être définie dans un fichier `.env` pour
remplacer la valeur par défaut. Le fichier `.env` est ignoré par Git.

## Transformations dbt

Le projet dbt se trouve dans `transform_meteo/`. Il doit utiliser la même base
PostgreSQL que l'API et disposer d'un profil nommé `transform_meteo`.

En local, créer d'abord le profil à partir de l'exemple :

```bash
copy transform_meteo\profiles.yml.example transform_meteo\profiles.yml
```

Depuis le répertoire du projet dbt, avec dbt installé localement :

```bash
cd transform_meteo
dbt debug
dbt run
dbt test
```

Dans le DAG Airflow, les tâches sont exécutées dans une chaîne unique :

```text
ingest_all_cities_task
  >> dbt_run_silver
  >> dbt_test_silver
  >> dbt_run_gold
  >> dbt_test_gold
```

Ainsi, une erreur d'ingestion bloque toutes les transformations dbt, et une
erreur de test Silver empêche de construire Gold. Le modèle incrémental est
construit depuis la table Bronze `public.weather_measurements`. Une exécution
complète peut être demandée lorsqu'une reconstruction de la table Silver est
nécessaire :

```bash
dbt run --full-refresh
```

## Tester le DAG et vérifier les tables

Après `docker compose up -d --build` :

1. Ouvrir Airflow sur <http://127.0.0.1:8080> et se connecter avec le compte
   de développement `admin` / `admin`.
2. Ouvrir le DAG `weather_batch_ingestion_dag`, puis l'onglet **Graph**.
   Le graphe doit afficher l'ingestion suivie de `dbt_run_silver`,
   `dbt_test_silver`, `dbt_run_gold` et `dbt_test_gold`.
3. Déclencher le DAG avec **Trigger DAG**. Attendre que les cinq tâches soient
   vertes. En cas d'échec, consulter les logs de la tâche concernée avant de
   relancer.
4. Vérifier les tables produites dans PostgreSQL :

```bash
docker exec -it appmeteo_db psql -U appmeteo -d appmeteo -c "SELECT COUNT(*) AS bronze_count FROM public.weather_measurements;"
docker exec -it appmeteo_db psql -U appmeteo -d appmeteo -c "SELECT COUNT(*) AS silver_count FROM silver.silver_weather;"
docker exec -it appmeteo_db psql -U appmeteo -d appmeteo -c "SELECT * FROM gold.mart_daily_weather_summary ORDER BY metric_date DESC, city_name ASC LIMIT 15;"
```

Les commandes dbt peuvent aussi être diagnostiquées dans le conteneur
Scheduler :

```bash
docker compose exec airflow-scheduler bash -lc "cd /opt/airflow/transform_meteo && dbt debug"
```

## Inspection de PostgreSQL

Afficher les dernières mesures :

```bash
docker exec -it appmeteo_db psql -U appmeteo -d appmeteo -c "SELECT id, city_name, temperature_2m, relative_humidity_2m, recorded_at FROM public.weather_measurements ORDER BY id DESC LIMIT 15;"
```

Afficher la structure de la table Bronze :

```bash
docker exec -it appmeteo_db psql -U appmeteo -d appmeteo -c "\d public.weather_measurements"
```

Après une exécution dbt, vérifier les tables Silver et Gold :

```bash
docker exec -it appmeteo_db psql -U appmeteo -d appmeteo -c "SELECT * FROM silver.silver_weather ORDER BY recorded_at DESC LIMIT 15;"
```

```bash
docker exec -it appmeteo_db psql -U appmeteo -d appmeteo -c "SELECT * FROM gold.mart_daily_weather_summary ORDER BY metric_date DESC, city_name ASC LIMIT 15;"
```

## Tests

Lancer la suite de tests Python :

```bash
uv run pytest
```

Les tests couvrent notamment la validation des coordonnées et les réponses de
l'API en cas de succès ou d'indisponibilité d'Open-Meteo.
