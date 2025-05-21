# TestDataBot - Main Makefile

# Default goal
.DEFAULT_GOAL := help

# Variables
APP_NAME := testdatabot
GO_FILES := $(shell find . -name "*.go" -not -path "./vendor/*")
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")

# Help message
help:
	@echo "TestDataBot - Makefile Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  help          Display this help message"
	@echo "  build         Build the application"
	@echo "  run           Run the application locally"
	@echo "  test          Run tests"
	@echo "  lint          Run linters"
	@echo "  clean         Clean build artifacts"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run Docker container"
	@echo "  deploy        Deploy to production"

# Build the application
build:
	@echo "Building $(APP_NAME)..."
	go build -v -ldflags="-X main.Version=$(VERSION)" -o bin/$(APP_NAME) .

# Run the application
run:
	@echo "Running $(APP_NAME)..."
	go run .

# Run tests
test:
	@echo "Running tests..."
	go test -v ./...

# Run linters
lint:
	@echo "Running linters..."
	@if command -v golangci-lint > /dev/null; then \
		golangci-lint run; \
	else \
		echo "golangci-lint not installed. Installing..."; \
		go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest; \
		golangci-lint run; \
	fi

# Clean build artifacts
clean:
	@echo "Cleaning..."
	rm -rf bin/
	go clean

# Build Docker image
docker-build:
	@echo "Building Docker image..."
	docker build -t $(APP_NAME):$(VERSION) .

# Run Docker container
docker-run:
	@echo "Running Docker container..."
	docker run -p 8080:8080 $(APP_NAME):$(VERSION)

# Deploy to production
deploy:
	@echo "Deploying to production..."
	netlify deploy --prod

.PHONY: help build run test lint clean docker-build docker-run deploy