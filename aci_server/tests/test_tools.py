import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..integrations.common.schema_generation.openai.validate import validate_tool_schema

client = TestClient(app)

## haven't tested, but should work :/
def test_tools_schema_validation():
    """
    Test that all tool schemas returned by /tools endpoint are valid according to OpenAI's schema
    """
    response = client.get("/tools")
    assert response.status_code == 200
    
    tools_data = response.json()["tools"]
    
    # Track any validation errors by integration
    validation_failures = {}
    
    for service_name, tool_schemas in tools_data.items():
        service_errors = []
        
        for tool_schema in tool_schemas:
            validation_errors = validate_tool_schema(tool_schema)
            if validation_errors:
                service_errors.append({
                    "tool": tool_schema.get("name", "unknown"),
                    "errors": validation_errors
                })
        
        if service_errors:
            validation_failures[service_name] = service_errors
    
    # If we found any validation errors, format them nicely and fail the test
    if validation_failures:
        error_message = "Tool schema validation failures:\n"
        for service, errors in validation_failures.items():
            error_message += f"\n{service}:\n"
            for error in errors:
                error_message += f"  Tool '{error['tool']}':\n"
                for validation_error in error['errors']:
                    error_message += f"    - {validation_error}\n"
        
        pytest.fail(error_message)