FROM python:3.11-slim

# Environment sanity
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (keep minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Disable venvs inside container
RUN poetry config virtualenvs.create false

# Copy dependency files first (better caching)
COPY pyproject.toml poetry.lock* /app/

# Install prod dependencies only
RUN poetry install --no-root --only main

# Copy project
COPY . /app

# Expose is optional on Render, but good practice
EXPOSE 8000

# Run app (Render provides $PORT)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}", "--proxy-headers", "--forwarded-allow-ips", "*"]
