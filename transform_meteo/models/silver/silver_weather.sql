{{
    config(
        materialized='incremental',
        unique_key='id'
    )
}}

with source as (
    -- On va chercher les données brutes de la table Bronze (via airflow)
    select * from public.weather_measurements
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
        -- On récupère uniquement les nouvelles mesures plus récentes que le max déjà stocké
        and recorded_at > (select max(recorded_at) from {{ this }})
    {% endif %}
)

select * from cleaned