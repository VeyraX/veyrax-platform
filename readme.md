How to Run IntegrationTests (aka let's pray if it is working)

1. Run all tests in Docker
docker-compose up --build test
2. Run tests for a specific integration
docker-compose run --rm test my_integration
3. Clean up containers after running tests
docker-compose down --volumes
