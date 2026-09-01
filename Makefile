.PHONY: dev dev-be dev-fe build clean

# Run both backend and frontend concurrently
dev:
	@echo "Starting backend (port 9000) and frontend (port 5173)..."
	@make -j2 dev-be dev-fe

# Backend only
dev-be:
	cd backend && .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

# Frontend only
dev-fe:
	cd frontend && npm run dev

# Build frontend for production
build:
	cd frontend && npm run build

# Kill any running dev servers on the expected ports
clean:
	@lsof -ti:9000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:5173 | xargs kill -9 2>/dev/null || true
	@echo "Ports 9000 and 5173 cleared."
