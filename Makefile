.PHONY: back front up clean help restart_back logs terminal debug build_front deploy_front

# Default target
all: help

# Install dependencies and run the frontend dev server
front:
	@echo "Setting up and running frontend..."
	cd frontend && npm install
	cd frontend && npm run dev

# Build the frontend application for production
build_front:
	@echo "Building frontend for production..."
	cd frontend && npm install
	cd frontend && rm -rf dist tsconfig.tsbuildinfo
	cd frontend && npm run build
	@echo "Frontend build completed. Production files are in frontend/dist directory."

# Build and deploy the frontend to AWS S3
deploy_front:
	@echo "Building and deploying frontend to S3..."
	# First build the frontend
	$(MAKE) build_front
	
	# Sync the built frontend to the S3 bucket
	@echo "Uploading to S3 bucket app.tecfis.com..."
	aws s3 sync frontend/dist/ s3://app.tecfis.com/ --delete
	
	# Invalidate CloudFront cache if needed
	@echo "Invalidating CloudFront cache..."
	DISTRIBUTION_ID=$$(aws cloudfront list-distributions --query "DistributionList.Items[?Aliases.Items[?contains(@, 'app.tecfis.com')]].Id" --output text) && \
	if [ ! -z "$$DISTRIBUTION_ID" ]; then \
		aws cloudfront create-invalidation --distribution-id $$DISTRIBUTION_ID --paths "/*"; \
	else \
		echo "No CloudFront distribution found for app.tecfis.com"; \
	fi
	
	@echo "Frontend deployment completed. Visit https://app.tecfis.com to see the changes."

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
	@echo "  make back         - Build and run the backend Docker container"
	@echo "  make front        - Install dependencies and run the frontend dev server"
	@echo "  make build_front  - Build the frontend for production"
	@echo "  make deploy_front - Build and deploy the frontend to AWS S3 (app.tecfis.com)"
	@echo "  make up           - Run both backend and frontend services"
	@echo "  make clean        - Remove Docker containers and images"
	@echo "  make debug        - Run backend in interactive mode for ipdb debugging"
	@echo "  make help         - Display this help message"

deploy:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 409439538115.dkr.ecr.us-east-1.amazonaws.com
	docker build --platform linux/amd64 -t tecfis backend
	docker tag tecfis:latest 409439538115.dkr.ecr.us-east-1.amazonaws.com/tecfis:latest	
	docker push 409439538115.dkr.ecr.us-east-1.amazonaws.com/tecfis:latest

back:
	@echo "Building and running backend container..."
	docker build --platform linux/arm64 -t tecfis backend
	docker stop tecfis 2>/dev/null || true
	docker rm tecfis 2>/dev/null || true
	docker run --name tecfis \
		-p 8080:8080 \
		-v $(PWD)/backend:/app \
		-d tecfis
	@echo "Backend running at http://localhost:8080"

restart_back:
	docker rm -f tecfis 2>/dev/null || true
	docker run --name tecfis \
		-p 8080:8080 \
		-v $(PWD)/backend:/app \
		-v pyconodig-data:/app/data \
		-d tecfis

debug:
	@echo "Running backend in debug mode with ipdb support..."
	docker stop tecfis 2>/dev/null || true
	docker rm tecfis 2>/dev/null || true
	docker run --name tecfis \
		-p 8080:8080 \
		-v $(PWD)/backend:/app \
		-v pyconodig-data:/app/data \
		-it tecfis

logs:
	@echo "Showing backend container logs..."
	docker logs -f tecfis

terminal:
	@echo "Opening terminal in backend container..."
	docker exec -it tecfis /bin/bash

lint:
	docker exec tecfis ruff check /app --fix --unsafe-fixes
	docker exec tecfis black /app
