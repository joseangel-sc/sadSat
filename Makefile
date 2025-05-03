.PHONY: back front up clean help

# Default target
all: help

# Build and run the backend Docker container
back:
	@echo "Building and running backend container..."
	docker build -t pyconodig-backend ./backend
	docker stop pyconodig-backend-container 2>/dev/null || true
	docker rm pyconodig-backend-container 2>/dev/null || true
	docker run --name pyconodig-backend-container \
		-p 8000:8000 \
		-v $(PWD)/backend:/app \
		-v pyconodig-data:/app/data \
		-d pyconodig-backend
	@echo "Backend running at http://localhost:8000"


# Install dependencies and run the frontend dev server
front:
	@echo "Setting up and running frontend..."
	cd frontend && npm install
	cd frontend && npm run dev

# Run both services in parallel
up:
	@echo "Starting both backend and frontend services..."
	$(MAKE) back
	@echo "Starting frontend..."
	cd frontend && npm install && npm run dev

# Clean up containers and build artifacts
clean:
	@echo "Cleaning up..."
	docker stop pyconodig-backend-container 2>/dev/null || true
	docker rm pyconodig-backend-container 2>/dev/null || true
	docker rmi pyconodig-backend 2>/dev/null || true
	@echo "Cleaned up Docker resources"

# Display help information
help:
	@echo "Available commands:"
	@echo "  make back   - Build and run the backend Docker container"
	@echo "  make front  - Install dependencies and run the frontend dev server"
	@echo "  make up     - Run both backend and frontend services"
	@echo "  make clean  - Remove Docker containers and images"
	@echo "  make help   - Display this help message"

