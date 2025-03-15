import requests
from typing import Dict, Any, Optional

class HttpClient:
    def __init__(self):
        pass

    def _replace_variables(self, text: str, variables: Dict[str, str]) -> str:
        if not variables:
            return text
            
        for key, value in variables.items():
            text = text.replace(f"{{{{{key}}}}}", value)
        return text

    def _prepare_headers(self, headers: list, variables: Dict[str, str]) -> Dict[str, str]:
        result = {}
        for header in headers:
            if not header.get("disabled", False):
                key = self._replace_variables(header["key"], variables)
                value = self._replace_variables(header["value"], variables)
                result[key] = value
        return result

    def _prepare_body(self, body: Dict[str, Any], variables: Dict[str, str]) -> Any:
        if not body:
            return None

        mode = body.get("mode")
        if mode == "raw":
            return self._replace_variables(body.get("raw", ""), variables)
        elif mode == "urlencoded":
            return [(item["key"], self._replace_variables(item["value"], variables)) 
                   for item in body.get("urlencoded", [])]
        elif mode == "formdata":
            return [(item["key"], self._replace_variables(item["value"], variables)) 
                   for item in body.get("formdata", [])]
        return None

    def execute_request(self, request_data: Dict[str, Any], environment: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        variables = environment or {}
        
        url = request_data["url"] if isinstance(request_data["url"], str) else request_data["url"]["raw"]
        url = self._replace_variables(url, variables)
        
        if "localhost" in url or "127.0.0.1" in url:
            return {
                "status": "Error",
                "code": 400,
                "headers": {},
                "data": {
                    "error": "Cannot make requests to localhost directly",
                    "solution": "For local development:",
                    "steps": [
                        "1. Download ngrok from https://ngrok.com",
                        "2. Start your local server (e.g., on port 3000)",
                        "3. Run: ngrok http 3000",
                        "4. Use the https URL from ngrok in your request"
                    ],
                    "example": {
                        "original_url": url,
                        "use_instead": "https://your-ngrok-url.ngrok.io/your-endpoint"
                    }
                }
            }
        
        headers = self._prepare_headers(request_data.get("headers", []), variables)
        body = self._prepare_body(request_data.get("body"), variables)
        
        try:
            response = requests.request(
                method=request_data["method"],
                url=url,
                headers=headers,
                data=body,
                timeout=30
            )
            
            result = {
                "status": response.reason,
                "code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
            
            return result
            
        except requests.exceptions.Timeout:
            return {
                "status": "Error",
                "code": 504,
                "headers": {},
                "data": {"error": "Request timed out after 30 seconds"}
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "Error",
                "code": 502,
                "headers": {},
                "data": {
                    "error": "Failed to connect to server",
                    "tips": [
                        "Check if the server is running",
                        "Verify the URL is correct",
                        "If testing locally, make sure to use ngrok"
                    ]
                }
            }
        except Exception as e:
            return {
                "status": "Error",
                "code": 500,
                "headers": {},
                "data": {"error": str(e)}
            }