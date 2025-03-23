export const OPENAPI_SPEC = {
  "openapi": "3.1.0",
  "info": {
    "title": "VeyraX API",
    "version": "1.0.1",
    "description": "API for retrieving available tools and dynamically executing tool methods."
  },
  "servers": [
    {
      "url": "https://veyraxapp.com",
      "description": "VeyraX Production Server"
    }
  ],
  "components": {
    "securitySchemes": {
      "VeyraxApiKey": {
        "type": "apiKey",
        "in": "header",
        "name": "VEYRAX_API_KEY"
      }
    },
    "schemas": {
      "ToolListResponse": {
        "type": "object",
        "properties": {
          "tools": {
            "type": "object",
            "additionalProperties": {
              "type": "object",
              "properties": {
                "methods": {
                  "type": "object",
                  "additionalProperties": {
                    "type": "object",
                    "properties": {
                      "parameters": {
                        "type": "object",
                        "additionalProperties": {
                          "type": "string"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      "DynamicToolMethodRequest": {
        "type": "object",
        "description": "Parameters for the specific tool method",
        "properties": {
          "tool": {
            "type": "string",
            "description": "The name of the tool (e.g., \"gmail\", \"slack\")"
          },
          "method": {
            "type": "string",
            "description": "The method of the tool (e.g., \"sendEmail\", \"listEvents\")"
          },
          "params": {
            "type": "object",
            "description": "Parameters to pass to the tool method",
            "additionalProperties": true
          }
        },
        "required": ["tool", "method"],
        "example": {
          "tool": "gmail",
          "method": "sendEmail",
          "params": {
            "to": "recipient@example.com",
            "subject": "Hello from VeyraX",
            "body": "This is a test email sent via the VeyraX API."
          }
        }
      },
      "DynamicToolMethodResponse": {
        "type": "object",
        "description": "Dynamic response from tool method",
        "properties": {
          "result": {
            "type": "string",
            "description": "A message or result from the tool"
          }
        },
        "additionalProperties": true
      }
    }
  },
  "paths": {
    "/get-tools": {
      "get": {
        "summary": "Retrieve available tools",
        "operationId": "getTools",
        "security": [
          {
            "VeyraxApiKey": []
          }
        ],
        "responses": {
          "200": {
            "description": "Successfully retrieved tools",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ToolListResponse"
                }
              }
            }
          },
          "500": {
            "description": "Server error"
          }
        }
      }
    },
    "/tool-execute": {
      "post": {
        "summary": "Executes a tool method using parameters from the request body",
        "operationId": "executeTool",
        "security": [
          {
            "VeyraxApiKey": []
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/DynamicToolMethodRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful response from tool method",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/DynamicToolMethodResponse"
                }
              }
            }
          },
          "400": {
            "description": "Invalid request format or missing fields"
          },
          "404": {
            "description": "Tool or method not found"
          },
          "500": {
            "description": "Internal server error"
          }
        }
      }
    }
  }
};

export const getOpenApiSpecAsString = (): string => {
  return JSON.stringify(OPENAPI_SPEC, null, 2);
};
