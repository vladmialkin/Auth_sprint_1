FROM python:3.12.4-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update -y && \
    apt install -y python3-dev \
    gcc \
    musl-dev

COPY pyproject.toml /

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY /src/* /app/src/