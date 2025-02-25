import json
from typing import Any, Dict, List

# List of unsupported keywords in strict mode
UNSUPPORTED_KEYWORDS = {
    "minLength", "maxLength", "pattern", "format",
    "minimum", "maximum", "multipleOf",
    "patternProperties", "unevaluatedProperties", "propertyNames", "minProperties", "maxProperties",
    "unevaluatedItems", "contains", "minContains", "maxContains", "minItems", "maxItems", "uniqueItems"
}

def validate_object_schema(schema: Dict[str, Any], is_strict: bool) -> List[str]:
    errors = []
    # Ensure the type is "object"
    if schema.get("type") != "object":
        errors.append("Expected type 'object'.")
    # In strict mode, additionalProperties must be explicitly false;
    # in non-strict mode, additionalProperties should not be set at all.
    if is_strict:
        if schema.get("additionalProperties") is not False:
            errors.append("'additionalProperties' must be set to false.")
    else:
        if "additionalProperties" in schema:
            errors.append("'additionalProperties' should not be set in non-strict mode.")
    # Check for unsupported keywords at this level
    for key in schema:
        if key in UNSUPPORTED_KEYWORDS:
            errors.append(f"Unsupported keyword '{key}' found.")
    # Ensure every property is marked as required
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    if is_strict:
        for prop in properties:
            if prop not in required:
                errors.append(f"Property '{prop}' is not listed in 'required'.")
    # Recursively validate each property's schema
    for prop_schema in properties.values():
        errors.extend(validate_schema(prop_schema, is_strict))
    # Validate "items" field for arrays, if present
    if "items" in schema:
        items_field = schema["items"]
        if isinstance(items_field, dict):
            errors.extend(validate_schema(items_field, is_strict))
        elif isinstance(items_field, list):
            for item in items_field:
                errors.extend(validate_schema(item, is_strict))
    return errors

def validate_union_schema(schema: Dict[str, Any], is_strict: bool) -> List[str]:
    errors = []
    types = schema.get("type")
    if isinstance(types, list):
        for t in types:
            if isinstance(t, dict):
                errors.extend(validate_schema(t, is_strict))
    return errors

def validate_schema(schema: Any, is_strict: bool) -> List[str]:
    errors = []
    if not isinstance(schema, dict):
        return errors
    # Check for unsupported keywords at this level
    for key in schema:
        if key in UNSUPPORTED_KEYWORDS:
            errors.append(f"Unsupported keyword '{key}' found.")
    # Handle union types (e.g. [ "null", "string" ])
    if "type" in schema and isinstance(schema["type"], list):
        errors.extend(validate_union_schema(schema, is_strict))
    elif schema.get("type") == "object":
        errors.extend(validate_object_schema(schema, is_strict))
    elif schema.get("type") == "array":
        if "items" in schema:
            errors.extend(validate_schema(schema["items"], is_strict))
    # Validate anyOf options if present
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            errors.extend(validate_schema(option, is_strict))
    return errors

def validate_tool_schema(tool_schema: Dict[str, Any]) -> List[str]:
    """
    Validate a tool schema (of type "function") against strict mode requirements.
    Expects a dictionary like:
    
      {
          "type": "function",
          "function": {
              "name": "...",
              "description": "...",
              "parameters": { ... },
              "strict": true/false
          }
      }
      
    For strict mode, nested object schemas must have additionalProperties explicitly false.
    For non-strict mode, the schema should not define additionalProperties.
    """
    errors = []
    if tool_schema.get("type") != "function":
        errors.append("Tool schema must have type 'function'.")
    func_obj = tool_schema.get("function")
    if not func_obj:
        errors.append("Tool schema must contain a 'function' key.")
        return errors
    # Ensure required keys exist in the function object
    for key in ["name", "description", "parameters", "strict"]:
        if key not in func_obj:
            errors.append(f"Missing '{key}' in function definition.")
    # Check that strict mode is defined and pass its value to the parameter validation.
    strict_value = func_obj.get("strict")
    if strict_value is True:
        errors.extend(validate_schema(func_obj.get("parameters"), is_strict=True))
    elif strict_value is False:
        errors.extend(validate_schema(func_obj.get("parameters"), is_strict=False))
    else:
        errors.append("Function schema 'strict' must be either true or false.")
    return errors

# Example usage:
if __name__ == "__main__":
    # Here is an example tool_schema to validate:
    example_tool_schema = {
        "type": "function",
        "function": {
            "name": "get_messages",
            "description": "Handle GET /gmail/messages",
            "parameters": {
                "type": "object",
                "properties": {
                    "pageToken": {
                        "type": ["null", "string"],
                        "description": "Parameter: pageToken"
                    },
                    "filters": {
                        "type": ["null", "object"],
                        "description": "Parameter: filters",
                        "properties": {
                            "body_keywords": {
                                "description": "Field: body_keywords",
                                "type": ["null", "string"]
                            },
                            "recipient": {
                                "description": "Field: recipient",
                                "type": ["null", "string"]
                            },
                            "subject_keywords": {
                                "description": "Field: subject_keywords",
                                "type": ["null", "string"]
                            },
                            "after_date": {
                                "description": "Field: after_date",
                                "type": ["null", "string"]
                            },
                            "before_date": {
                                "description": "Field: before_date",
                                "type": ["null", "string"]
                            },
                            "max_results": {
                                "description": "Field: max_results",
                                "type": ["null", "integer"]
                            }
                        },
                        "required": [
                            "body_keywords",
                            "recipient",
                            "subject_keywords",
                            "after_date",
                            "before_date",
                            "max_results"
                        ],
                        "additionalProperties": False
                    }
                },
                "required": ["pageToken", "filters"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
    
    validation_errors = validate_tool_schema(example_tool_schema)
    if validation_errors:
        print("Validation errors:")
        for error in validation_errors:
            print(" -", error)
    else:
        print("Tool schema validation passed with no errors.")


# if __name__ == "__main__":
#     from aci_server.main import get_tools
#     tools = get_tools()

#     for tool in tools:
#         for service_name, tool_schema in tool.items():
#             errors = validate_tool_schema(tool_schema)
#             if len(errors) > 0:
#                 print(tool, errors)