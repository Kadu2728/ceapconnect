# syntax=docker/dockerfile:1

# =============================================================================
# Stage 1 — builder: instala as dependências de produção em um virtualenv
# isolado. Dependências de sistema necessárias apenas para compilar pacotes
# Python (ex.: cryptography) ficam restritas a este stage e não vazam para a
# imagem final.
# =============================================================================
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Copia apenas o requirements.txt primeiro para aproveitar o cache de layers
# do Docker — a reinstalação de dependências só é disparada quando esse
# arquivo muda, não a cada alteração de código.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# =============================================================================
# Stage 2 — runtime: imagem final enxuta, sem toolchain de build, rodando
# como usuário não-root.
# =============================================================================
FROM python:3.13-slim AS runtime

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --chown=app:app . .

USER app

EXPOSE 8000

# Antes de subir o servidor, roda as migrations pendentes do Alembic — garante
# que o schema do banco em produção nunca fique dessincronizado do código
# implantado. `$PORT` é respeitado quando a plataforma o injeta (Render,
# Railway); no docker-compose local, é definido explicitamente no serviço.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${UVICORN_WORKERS:-2}"]
