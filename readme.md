Configuration

1. Backend: `cp .env.example .env` and fill in the values you need.
2. Frontend: `cp main/.env.example main/.env.local` and fill in the values you need.
3. Never commit real `.env` files — they are git-ignored.

How to Run IntegrationTests (aka let's pray if it is working)

1. Run all tests in Docker
docker-compose exec aci_server /app/run_tests.sh

2. Run tests for a specific integration
docker-compose exec aci_server /app/run_tests.sh dropbox
