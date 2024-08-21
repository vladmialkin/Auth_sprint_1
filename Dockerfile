FROM python:3.12.4-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка python3-dev и gcc с использованием --no-install-recommends
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends python3-dev=3.12.4-1 gcc musl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование файлов
COPY pyproject.toml /

# Обновление pip и установка Poetry с использованием --no-cache-dir
RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Копирование кода приложения
COPY /src/* /app/src/
