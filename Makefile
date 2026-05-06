.PHONY: install run-backend run-frontend stop-backend stop-frontend stop dev clean

# Install all dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run backend
run-backend:
	@echo "Starting backend..."
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload

# Run frontend
run-frontend:
	@echo "Starting frontend..."
	cd frontend && npm run dev

# Stop backend (Port 8000)
stop-backend:
	@echo "Stopping backend..."
	-lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Stop frontend (Port 5173 and 5174)
stop-frontend:
	@echo "Stopping frontend..."
	-lsof -ti:5173 | xargs kill -9 2>/dev/null || true
	-lsof -ti:5174 | xargs kill -9 2>/dev/null || true

# Stop everything
stop: stop-backend stop-frontend
	@echo "All services stopped."

# Run both in background
dev:
	@echo "Starting both backend and frontend..."
	make run-backend & make run-frontend

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf backend/venv
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf backend/aren.db
	rm -rf backend/uploads/*
