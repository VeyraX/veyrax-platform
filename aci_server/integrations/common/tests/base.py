import os
import pytest
from fastapi.testclient import TestClient
from aci_server.healthcheck.utils.utils import login_to_supabase
from aci_server.main import app
from pydantic import ConfigDict

class BaseIntegrationTest:
    model_config = ConfigDict()  # Modern way to configure Pydantic models
    
    @classmethod
    def setup_class(cls):
        cls.api_url = os.getenv('NEXT_PUBLIC_API_URL')
        if not cls.api_url:
            pytest.skip("NEXT_PUBLIC_API_URL not configured")
        cls.access_token, _ = login_to_supabase()
        cls.client = TestClient(app)

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    # New helper methods
    def _make_request(self, method, route_suffix, payload=None, expected_status=200):
        url = f"{self.api_url}/{route_suffix.lstrip('/')}"
        response = method(
            url,
            headers=self.get_headers(),
            json=payload or {}
        )

        if expected_status:
            assert response.status_code == expected_status, (
                f"Route {route_suffix} failed. "
                f"Expected {expected_status}, got {response.status_code}. "
                f"Response: {response.text}"
            )
        return response

    def post(self, route_suffix, payload=None, expected_status=200):
        return self._make_request(self.client.post, route_suffix, payload, expected_status)

    def get(self, route_suffix, payload=None, expected_status=200):
        return self._make_request(self.client.get, route_suffix, payload, expected_status)

    def put(self, route_suffix, payload=None, expected_status=200):
        return self._make_request(self.client.put, route_suffix, payload, expected_status)

    def delete(self, route_suffix, payload=None, expected_status=200):
        return self._make_request(self.client.delete, route_suffix, payload, expected_status)

@pytest.fixture(scope="module")
def base_setup():
    test_setup = BaseIntegrationTest()
    test_setup.setup_class()
    return test_setup