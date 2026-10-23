FROM apache/airflow:2.9.1-python3.12

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir \
    dbt-core==1.8.2 \
    dbt-postgres==1.8.2
