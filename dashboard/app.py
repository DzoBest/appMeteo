import os
from contextlib import closing

import pandas as pd
import psycopg2
import streamlit as st


st.set_page_config(
    page_title="AppMeteo",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .hero {
        padding: 1.5rem 1.75rem;
        border-radius: 1rem;
        background: linear-gradient(135deg, #0f766e, #2563eb);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 { margin: 0; font-size: 2.2rem; }
    .hero p { margin: .45rem 0 0; opacity: .9; }
    [data-testid="stMetric"] {
        border: 1px solid rgba(100, 116, 139, .2);
        border-radius: .75rem;
        padding: .75rem;
        background: rgba(248, 250, 252, .65);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_connection():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "appmeteo"),
        user=os.getenv("DB_USER", "appmeteo"),
        password=os.getenv("DB_PASSWORD", "appmeteo"),
        connect_timeout=5,
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("SET default_transaction_read_only = on")
    return connection


def read_query(query: str, parameters: tuple = ()) -> pd.DataFrame:
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
    return pd.DataFrame(rows, columns=columns)


@st.cache_data(ttl=300)
def load_cities() -> list[str]:
    data = read_query(
        """
        SELECT DISTINCT city_name
        FROM silver.silver_weather
        WHERE city_name IS NOT NULL
        ORDER BY city_name
        """
    )
    return data["city_name"].tolist()


@st.cache_data(ttl=60)
def load_recent_weather(city: str) -> pd.DataFrame:
    return read_query(
        """
        SELECT recorded_at, temperature_2m, relative_humidity_2m
        FROM silver.silver_weather
        WHERE city_name = %s
        ORDER BY recorded_at DESC
        LIMIT 48
        """,
        (city,),
    ).sort_values("recorded_at")


@st.cache_data(ttl=60)
def load_daily_summary(city: str) -> pd.DataFrame:
    return read_query(
        """
        SELECT metric_date, min_temperature, avg_temperature,
               max_temperature, avg_humidity, total_measurements
        FROM gold.mart_daily_weather_summary
        WHERE city_name = %s
        ORDER BY metric_date DESC
        LIMIT 14
        """,
        (city,),
    )


@st.cache_data(ttl=60)
def load_freshness(city: str) -> pd.DataFrame:
    return read_query(
        """
        SELECT MAX(recorded_at) AS last_update,
               COUNT(*) FILTER (WHERE recorded_at::date = CURRENT_DATE)
                 AS measurements_today
        FROM silver.silver_weather
        WHERE city_name = %s
        """,
        (city,),
    )


def format_timestamp(value) -> str:
    if pd.isna(value):
        return "Aucune donnée"
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert("Europe/Paris")
    return timestamp.strftime("%d/%m/%Y à %H:%M")


st.markdown(
    """
    <div class="hero">
        <h1>🌤️ AppMeteo</h1>
        <p>Suivez les mesures météo et la fraîcheur de votre pipeline data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Exploration")
    st.caption("Choisissez une ville pour afficher ses dernières données.")
    if st.button("Actualiser les données", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

try:
    cities = load_cities()
except Exception as error:
    st.error(
        "Impossible de charger les villes. Vérifiez que PostgreSQL, "
        "la table Silver et Docker Compose sont disponibles."
    )
    st.exception(error)
    st.stop()

if not cities:
    st.info("Aucune ville n'est encore disponible. Lancez le pipeline Airflow.")
    st.stop()

with st.sidebar:
    city = st.selectbox("Ville", cities)

try:
    freshness = load_freshness(city).iloc[0]
    recent_weather = load_recent_weather(city)
    daily_summary = load_daily_summary(city)
except Exception as error:
    st.error(
        "Les données de cette ville ne sont pas disponibles. "
        "Vérifiez l'exécution des modèles dbt Silver et Gold."
    )
    st.exception(error)
    st.stop()

last_update = format_timestamp(freshness["last_update"])
measurements_today = int(freshness["measurements_today"])

st.subheader(f"Vue d'ensemble — {city}")
metric_columns = st.columns(3)
metric_columns[0].metric("Dernière mise à jour", last_update)
metric_columns[1].metric("Mesures aujourd'hui", measurements_today)
metric_columns[2].metric("Mesures affichées", len(recent_weather))

if pd.notna(freshness["last_update"]):
    last_update_timestamp = pd.Timestamp(freshness["last_update"])
    if last_update_timestamp.tzinfo is None:
        last_update_timestamp = last_update_timestamp.tz_localize("UTC")
    age = pd.Timestamp.now(tz="UTC") - last_update_timestamp.tz_convert("UTC")
    if age.total_seconds() > 3 * 3600:
        st.warning("Les dernières données datent de plus de trois heures.")
    else:
        st.success("Les données sont à jour.")

st.divider()

chart_column, summary_column = st.columns([1.35, 1])

with chart_column:
    st.subheader("Température récente")
    if recent_weather.empty:
        st.info("Aucune mesure récente pour cette ville.")
    else:
        chart_data = recent_weather.set_index("recorded_at")[["temperature_2m"]]
        st.line_chart(chart_data, y="temperature_2m", use_container_width=True)
        st.caption("Les 48 dernières mesures disponibles dans la couche Silver.")

with summary_column:
    st.subheader("Résumé du jour")
    if daily_summary.empty:
        st.info("Aucun agrégat Gold disponible pour cette ville.")
    else:
        latest = daily_summary.iloc[0]
        summary_columns = st.columns(3)
        summary_columns[0].metric("Minimum", f"{latest['min_temperature']:.1f} °C")
        summary_columns[1].metric("Moyenne", f"{latest['avg_temperature']:.1f} °C")
        summary_columns[2].metric("Maximum", f"{latest['max_temperature']:.1f} °C")
        st.caption(f"Journée du {latest['metric_date']}")

st.subheader("Historique journalier")
if daily_summary.empty:
    st.info("L'historique Gold sera disponible après une exécution dbt.")
else:
    display_summary = daily_summary.rename(
        columns={
            "metric_date": "Date",
            "min_temperature": "Min (°C)",
            "avg_temperature": "Moyenne (°C)",
            "max_temperature": "Max (°C)",
            "avg_humidity": "Humidité moyenne (%)",
            "total_measurements": "Mesures",
        }
    )
    st.dataframe(
        display_summary,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Min (°C)": st.column_config.NumberColumn(format="%.1f"),
            "Moyenne (°C)": st.column_config.NumberColumn(format="%.1f"),
            "Max (°C)": st.column_config.NumberColumn(format="%.1f"),
            "Humidité moyenne (%)": st.column_config.NumberColumn(format="%.1f"),
        },
    )

st.caption("Source : PostgreSQL — couches Silver et Gold dbt.")
