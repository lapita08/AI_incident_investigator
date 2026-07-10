.PHONY: setup dev backend-dev frontend-dev test lint format typecheck seed demo docker-up docker-down clean

setup:
	cd backend && python -m pip install -e ".[dev]"
	cd frontend && corepack enable && pnpm install
	cd frontend && pnpm exec playwright install --with-deps chromium

dev:
	@echo "Start backend and frontend in separate terminals with: make backend-dev and make frontend-dev"

backend-dev:
	cd backend && PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd frontend && pnpm run dev

test:
	cd backend && PYTHONPATH=. pytest
	cd frontend && pnpm test

lint:
	cd backend && ruff check .
	cd frontend && pnpm run lint

format:
	cd backend && ruff format .
	cd frontend && pnpm run format

typecheck:
	cd backend && mypy app
	cd frontend && pnpm run build

seed:
	curl -X POST http://127.0.0.1:8000/api/v1/incidents/sample/db-latency-incident

demo:
	@echo "1. make backend-dev"
	@echo "2. make frontend-dev"
	@echo "3. Open http://127.0.0.1:5173 and load the DB latency demo"

docker-up:
	docker compose up --build

docker-down:
	docker compose down

clean:
	rm -f backend/incident_investigator.db
	rm -rf frontend/dist frontend/node_modules backend/.pytest_cache backend/.ruff_cache
