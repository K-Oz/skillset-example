# Builder stage
FROM golang:1.21-alpine AS builder

# Set up working directory
WORKDIR /app

# Install dependencies
RUN apk add --no-cache git ca-certificates tzdata

# Copy go.mod and go.sum
COPY go.mod ./
COPY go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags="-extldflags=-static" -o main .

# Final stage
FROM alpine:3.18

# Install CA certificates and timezone data
RUN apk --no-cache add ca-certificates tzdata

# Set up working directory
WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/main .

# Copy public directory
COPY public/ public/

# Expose port
EXPOSE 8080

# Run the application
CMD ["./main"]