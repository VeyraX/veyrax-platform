# WhatsApp Bridge Service

This service provides a bridge between your application and WhatsApp using a REST API.

## Development Setup

### Running locally without Docker

To run the service directly on your machine:

```bash
go run main.go
```

This will start the service on port 8080. WhatsApp data will be stored in the `./store` directory.

### Running with Docker Compose (Development)

The WhatsApp Bridge is included in the main docker-compose.yml file for local development.
Simply run the main docker-compose command from the root directory:

```bash
docker-compose up -d
```

This will start all services including the WhatsApp bridge. The bridge will be accessible at http://localhost:8080/api and from other containers as http://whatsapp-bridge:8080/api.

## Production Deployment

For production deployment, use the separate docker-compose file:

```bash
cd services/whatsapp-bridge
docker-compose -f docker-compose.prod.yml up -d
```

This will:
1. Build the WhatsApp bridge service
2. Start the container with port 8080 exposed
3. Mount a persistent volume for WhatsApp data
4. Configure automatic restarts

### Configuration

The service doesn't require specific configuration files. It stores all data in the `/app/store` directory which is mounted as a volume.

### Health Checks

The service includes a health check endpoint at `/api/status` which returns the current status of the WhatsApp connection.

## API Endpoints

- `GET /api/status`: Check the status of the WhatsApp connection
- `POST /api/auth`: Authenticate with WhatsApp (returns QR code)
- `POST /api/send`: Send a WhatsApp message
- More endpoints documented in the API documentation

## Data Persistence

WhatsApp data is stored in the `/app/store` directory, which is mapped to a Docker volume in both development and production setups. This ensures that connection data and message history persist across container restarts. 