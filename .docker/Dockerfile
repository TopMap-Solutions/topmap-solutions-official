# ==============================
# Stage 1: Python Builder
# ==============================

FROM python:3.12-slim-bookworm AS python-builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Create virtual environment
RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# Copy dependency files first for better Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies only
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application source
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev

# ==============================
# Stage 2: Runtime
# ==============================

FROM python:3.12-slim-bookworm

WORKDIR /app


# Copy virtual environment
COPY --from=python-builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Copy application
COPY . .


EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"]