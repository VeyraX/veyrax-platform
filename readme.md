How to Run IntegrationTests (aka let's pray if it is working)

1. Run all tests in Docker
docker-compose exec aci_server /app/run_tests.sh

2. Run tests for a specific integration
docker-compose exec aci_server /app/run_tests.sh dropbox
