from datetime import datetime, timedelta
import urllib.request
import json
from airflow import DAG
from airflow.operators.python import PythonOperator


def trigger_weather_ingest():
    """Appelle le endpoint d'ingestion batch de l'API FastAPI dans le réseau Docker."""
    api_url = "http://api:8000/weather/ingest"
    req = urllib.request.Request(api_url, method="POST")

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        print(f"Ingestion response: {result}")
        if response.status != 201:
            raise RuntimeError(f"Ingestion failed with status {response.status}: {result}")
        return result


default_args = {
    "owner": "appmeteo",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weather_batch_ingestion_dag",
    default_args=default_args,
    description="Orchestration de la collecte et de l'ingestion météo multi-villes toutes les heures",
    schedule_interval=timedelta(hours=1),  # Exécution toutes les 60 minutes
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["meteo", "ingestion", "bronze", "silver"],
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_all_cities_task",
        python_callable=trigger_weather_ingest,
    )

    ingest_task