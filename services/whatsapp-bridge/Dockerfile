FROM golang:1.20-alpine AS builder

WORKDIR /app

# Copy go mod and sum files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY main.go ./

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -o whatsapp-bridge main.go

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /app

# Copy the binary from builder stage
COPY --from=builder /app/whatsapp-bridge .

# Copy store directory if it exists and contains initial data
COPY store/ /app/store/

# Create store directory if needed
RUN mkdir -p /app/store

# Expose port
EXPOSE 8080

# Command to run
CMD ["./whatsapp-bridge"] 