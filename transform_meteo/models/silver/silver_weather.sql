{{
    config(
        materialized='incremental',
        unique_key='id'
    )
}}

with source as (
    -- On va chercher les données brutes de la table Bronze (via airflow)
    select * from {{ source('meteo_bronze', 'weather_measurements') }}
), 

cleaned as (
    -- On nettoie les données brutes
    select 
        id,
        temperature_2m,
        relative_humidity_2m,
        city_name,
        recorded_at
    from source
    where temperature_2m is not null and relative_humidity_2m is not null
    
    -- LA CONDITION INCRÉMENTALE PRO :
    {% if is_incremental() %}
        -- L'ingestion parallèle produit des timestamps légèrement différents
        -- selon les villes. L'id Bronze permet de conserver tout le lot.
        and id > (select coalesce(max(id), 0) from {{ this }})
    {% endif %}
)

select * from cleaned