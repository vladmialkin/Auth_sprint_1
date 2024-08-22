.PHONY: up down local lint migrations migrate

up:
	docker compose up --build

down:
	docker compose down -v --remove-orphans

local:
	docker compose -f local-docker-compose.yml up -d --build

lint:
	ruff format .
	ruff check . --fix --show-fixes


.DEFAULT_GOAL := up