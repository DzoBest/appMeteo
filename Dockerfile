# 1. Image de base : un Linux Debian allégé avec Python 3.12 préinstallé
FROM python:3.12-slim

# 2. Répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# 3. Installer l'outil "uv" pour gérer les dépendances ultra rapidement
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 4. Copier d'abord uniquement les fichiers de dépendances (optimisation du cache Docker)
COPY pyproject.toml uv.lock ./

# 5. Installer toutes les dépendances du projet sans installer le projet lui-même
RUN uv sync --frozen --no-install-project

# 6. Copier le reste du code source de votre application dans le conteneur
COPY src/ ./src/
COPY README.md ./

# 7. Finaliser l'installation du projet
RUN uv sync --frozen

# 8. Ajouter l'environnement virtuel créé par uv au PATH pour exécuter les commandes directement
ENV PATH="/app/.venv/bin:$PATH"

# 9. Exposer le port 8000 sur lequel tourne FastAPI
EXPOSE 8000

# 10. Commande exécutée au démarrage du conteneur pour lancer FastAPI
CMD ["uvicorn", "appmeteo.main:app", "--host", "0.0.0.0", "--port", "8000"]