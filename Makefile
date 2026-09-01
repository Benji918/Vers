.PHONY: dev dev-be dev-fe build clean

# Run both backend and frontend concurrently
dev:
	@echo "Starting backend (port 9000) and frontend (port 5173)..."
	@make -j2 dev-be dev-fe

# Backend only
dev-be:
	@echo "Starting backend (port 9000)..."
	cd backend && .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

# Frontend only
dev-fe:
	@echo "Starting frontend (port 5173)..."
	cd frontend && npm run dev

# Build frontend for production
build:
	@echo "Building frontend..."
	cd frontend && npm run build

# Kill any running dev servers on the expected ports
clean:
	@echo "Killing any running dev servers on ports 9000 and 5173..."
	@lsof -ti:9000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:5173 | xargs kill -9 2>/dev/null || true
	@echo "Ports 9000 and 5173 cleared."
