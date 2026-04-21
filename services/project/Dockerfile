# ── Stage 1 : Builder ─────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

COPY app/requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# ── Stage 2 : Runtime ─────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Création d'un utilisateur non-root (sécurité)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copie des dépendances installées depuis le builder
COPY --from=builder /root/.local /home/appuser/.local

# Copie du code source
COPY app/ .

# Permissions
RUN chown -R appuser:appuser /app

# Utilisation de l'utilisateur non-root
USER appuser

# Port du service
EXPOSE 8002

# Commande de démarrage
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]