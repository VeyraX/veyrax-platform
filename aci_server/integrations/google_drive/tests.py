from aci_server.integrations.common.tests.base import base_setup
import pytest

@pytest.fixture(scope="function")
def uploaded_url_file(base_setup):
    """Fixture that uploads a file from URL and deletes it after test"""
    payload = {
        "file": {
            "file_name": "neon_orb.webp",
            "file_content": {
                "file_url": "https://bulkimagegeneration.com/_next/image?url=%2Fuse-cases%2FCreative%20%26%20Entertainment%2Fgame%20objects%2FA_bright_orb_encompassed_by_swirling_neon_streaks_-7_compressed.webp&w=828&q=75"
            },
            "content_type": "image/webp"
        }
    }
    response = base_setup.post("/google-drive/upload_file", payload=payload)
    assert response.status_code == 200, "URL upload failed"
    resp_json = response.json()
    data = resp_json.get("data", {})
    file_id = data.get("id")
    assert file_id, "No file ID in response"
    
    yield data  # Provide file data to test
    
    # Cleanup
    delete_payload = {"file_id": file_id}
    delete_response = base_setup.post("/google-drive/delete_file", payload=delete_payload)
    assert delete_response.status_code == 200, "Failed to delete URL-uploaded file"

@pytest.fixture(scope="function")
def uploaded_base64_file(base_setup):
    """Fixture that uploads a file from base64 and deletes it after test"""
    payload = {
        "file": {
            "file_name": "sample_image.png",
            "file_content": {
                "file_base64": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII="
            },
            "content_type": "image/png"
        }
    }
    response = base_setup.post("/google-drive/upload_file", payload=payload)
    assert response.status_code == 200, "Base64 upload failed"
    resp_json = response.json()
    data = resp_json.get("data", {})
    file_id = data.get("id")
    assert file_id, "No file ID in response"
    
    yield data
    
    # Cleanup
    delete_payload = {"file_id": file_id}
    delete_response = base_setup.post("/google-drive/delete_file", payload=delete_payload)
    assert delete_response.status_code == 200, "Failed to delete base64-uploaded file"

def test_upload_from_url(uploaded_url_file):
    """Test file upload from URL"""
    file_data = uploaded_url_file
    assert file_data["name"] == "neon_orb.webp"
    assert "id" in file_data, "File ID missing in response"

def test_upload_from_base64(uploaded_base64_file):
    """Test file upload from base64"""
    file_data = uploaded_base64_file
    assert file_data["name"] == "sample_image.png"
    assert file_data["mime_type"] == "image/png"
    assert "id" in file_data, "File ID missing in response" 