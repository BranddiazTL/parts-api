FROM python:3.12-slim

WORKDIR /app

ENV POETRY_VERSION=2.1.2

RUN pip install "poetry==$POETRY_VERSION"

COPY ../pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main

COPY .. .

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 