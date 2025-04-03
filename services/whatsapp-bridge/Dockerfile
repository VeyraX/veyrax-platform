FROM golang:1.24-alpine AS builder

WORKDIR /app

# Install build dependencies including gcc and SQLite
RUN apk add --no-cache gcc musl-dev sqlite-dev

# Copy go mod and sum files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY main.go ./

# Build the application WITH CGO enabled
RUN CGO_ENABLED=1 GOOS=linux go build -o whatsapp-bridge main.go

# Final stage
FROM alpine:latest

# Install runtime dependencies for SQLite and CA certificates
RUN apk --no-cache add ca-certificates sqlite

WORKDIR /app

# Copy the binary from builder stage
COPY --from=builder /app/whatsapp-bridge .

# Create store directory if needed
RUN mkdir -p /app/store

# Expose port
EXPOSE 8080

# Command to run
CMD ["./whatsapp-bridge"] 