import os
import pytest
from fastapi.testclient import TestClient
from aci_server.healthcheck.utils.utils import login_to_supabase
from aci_server.main import app

class BaseIntegrationTest:
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

@pytest.fixture(scope="module")
def base_setup():
    test_setup = BaseIntegrationTest()
    test_setup.setup_class()
    return test_setup