export const OPENAPI_SPEC = {
  "info": {
    "title": "VeyraX API",
    "description": "API for retrieving available tools and executing tool methods dynamically.",
    "version": "1.0.0"
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
      "SendEmailRequest": {
        "type": "object",
        "properties": {
          "to": {
            "type": "string",
            "example": "recipient@example.com"
          },
          "subject": {
            "type": "string",
            "example": "Hello from VeyraX"
          },
          "body": {
            "type": "string",
            "example": "This is a test email sent via the VeyraX API."
          }
        },
        "required": [
          "to",
          "subject",
          "body"
        ]
      },
      "SendEmailResponse": {
        "type": "object",
        "properties": {
          "messageId": {
            "type": "string",
            "example": "1234567890"
          },
          "threadId": {
            "type": "string",
            "example": "0987654321"
          },
          "status": {
            "type": "string",
            "example": "sent"
          }
        }
      },
      "DynamicToolMethodRequest": {
        "type": "object",
        "description": "Generic request object for tool method execution.",
        "properties": {
          "parameters": {
            "type": "object",
            "additionalProperties": true,
            "description": "Dynamic parameters for the tool method."
          }
        },
        "required": [
          "parameters"
        ]
      },
      "DynamicToolMethodResponse": {
        "type": "object",
        "description": "Generic response object for tool method execution.",
        "properties": {
          "result": {
            "type": "object",
            "additionalProperties": true,
            "description": "Dynamic result structure based on the tool method."
          }
        }
      }
    }
  },
  "paths": {
    "/get-tools": {
      "get": {
        "operationId": "getTools",
        "summary": "Retrieve available tools",
        "description": "Fetches a list of available tools and their supported methods.",
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
          }
        }
      }
    },
    "/tool-call/{tool}/{method}?include_component=false": {
      "post": {
        "operationId": "callToolMethod",
        "summary": "Call a tool method dynamically",
        "description": "Executes a specified method on a given tool.",
        "security": [
          {
            "VeyraxApiKey": []
          }
        ],
        "parameters": [
          {
            "name": "tool",
            "in": "path",
            "required": true,
            "description": "The tool to execute (e.g., \"gmail\", \"google-calendar\").",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "method",
            "in": "path",
            "required": true,
            "description": "The method to execute within the tool (e.g., \"sendEmail\", \"listEvents\").",
            "schema": {
              "type": "string"
            }
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
            "description": "Successful tool method execution",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/DynamicToolMethodResponse"
                }
              }
            }
          }
        }
      }
    }
  }
};

export const getOpenApiSpecAsString = (): string => {
  return JSON.stringify(OPENAPI_SPEC, null, 2);
};
