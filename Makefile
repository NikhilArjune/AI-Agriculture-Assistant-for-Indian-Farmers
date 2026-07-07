.PHONY: up down build logs backend-shell setup-qdrant seed-schemes ingest-docs test lint

# Docker
up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

# Backend dev (local, no Docker)
backend-dev:
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

backend-shell:
	docker compose exec backend bash

# Frontend dev (local, no Docker)
frontend-dev:
	cd frontend && npm run dev

# Database setup
setup-qdrant:
	cd backend && python scripts/setup_qdrant.py

seed-schemes:
	cd backend && python scripts/seed_schemes.py

# Ingest docs: make ingest-docs DIR=data/docs TOPIC=crop_advisory
ingest-docs:
	cd backend && python scripts/ingest_documents.py --dir $(DIR) --topic $(TOPIC)

# Celery worker
worker:
	cd backend && celery -A workers.celery_app worker --loglevel=info

worker-beat:
	cd backend && celery -A workers.celery_app beat --loglevel=info

# Tests
test:
	cd backend && pytest tests/unit/ -v

test-integration:
	cd backend && pytest tests/integration/ -v

test-all:
	cd backend && pytest -v

# Code quality
lint:
	cd backend && ruff check . && ruff format --check .

lint-fix:
	cd backend && ruff check --fix . && ruff format .

type-check:
	cd backend && mypy .

# MCP server (standalone)
mcp-server:
	cd backend && python -m mcp.server
