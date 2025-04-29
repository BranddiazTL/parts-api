FROM python:3.12-slim

WORKDIR /app

ENV POETRY_VERSION=2.1.2

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends build-essential postgresql-client libpq-dev && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

COPY ../pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main

COPY .. .

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]