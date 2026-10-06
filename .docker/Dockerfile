# syntax=docker/dockerfile:1

# ==============================
# Stage 1: Python Builder
# ==============================

FROM python:3.14-slim-bookworm AS python-builder

WORKDIR /app

ARG UV_VERSION=0.11.13

RUN pip install --no-cache-dir "uv==${UV_VERSION}"

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY . .

RUN uv sync --frozen --no-dev


# ==============================
# Stage 2: Runtime
# ==============================

FROM python:3.14-slim-bookworm

WORKDIR /app

COPY --from=python-builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120"]
