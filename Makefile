.PHONY: back front up clean help restart_back logs terminal

# Default target
all: help

# Build and run the backend Docker container
build:
	@echo "Building and running backend container..."
	docker build --progress=plain --platform linux/arm64 -t tecfis-local backend
	docker stop pyconodig-backend-container 2>/dev/null || true
	docker rm pyconodig-backend-container 2>/dev/null || true
	docker run --name pyconodig-backend-container \
		-p 8080:8080 \
		-v $(PWD)/backend:/app \
		-v pyconodig-data:/app/data \
		-d pyconodig-backend
	@echo "Backend running at http://localhost:8080"


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


logs:
	@echo "Showing backend container logs..."
	docker logs -f pyconodig-backend-container

# Open a terminal in the running backend container
terminal:
	@echo "Opening terminal in backend container..."
	docker exec -it pyconodig-backend-container /bin/bash

# Restart the backend container with a fresh build
restart_back:
	docker rm -f pyconodig-backend-container 2>/dev/null || true
	docker run --name pyconodig-backend-container \
		-p 8080:8080 \
		-v $(PWD)/backend:/app \
		-v pyconodig-data:/app/data \
		-d pyconodig-backend
	@echo "Backend rebuilt and restarted at http://localhost:8080"


deploy:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 409439538115.dkr.ecr.us-east-1.amazonaws.com
	docker build --platform linux/amd64 -t tecfis backend
	docker tag tecfis:latest 409439538115.dkr.ecr.us-east-1.amazonaws.com/tecfis:latest	
	docker push 409439538115.dkr.ecr.us-east-1.amazonaws.com/tecfis:latest

lint:
	docker exec pyconodig-backend-container ruff check /app --fix --unsafe-fixes
	docker exec pyconodig-backend-container black /app
