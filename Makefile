.PHONY: install run-backend run-frontend dev clean

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

# Run both (using & to run in parallel in the same terminal, use Ctrl+C to stop)
dev:
	@echo "Starting both backend and frontend..."
	(cd backend && . venv/bin/activate && uvicorn app.main:app --reload) & \
	(cd frontend && npm run dev)

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf backend/venv
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf backend/aren.db
	rm -rf backend/uploads/*
