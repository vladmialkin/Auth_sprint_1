FROM python:3.12.4-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends python3-dev=3.12.4-1 gcc musl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /

RUN pip install --upgrade pip==24.2 && \
    pip install --no-cache-dir poetry==1.8.2 && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY /src/* /app/src/
