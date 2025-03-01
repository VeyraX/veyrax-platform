from integrations.common.tests.base import base_setup
import pytest
from integrations.google_drive.schema import PermissionRequest

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
def uploaded_text_file(base_setup):
    """Fixture that uploads a text file from base64 and deletes it after test"""
    payload = {
        "file": {
            "file_name": "test.txt",
            "file_content": {
                # This is base64 encoded "Hello, this is a test file!"
                "file_base64": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IGZpbGUh"
            },
            "content_type": "text/plain"
        }
    }
    response = base_setup.post("/google-drive/upload_file", payload=payload)
    assert response.status_code == 200, "Text file upload failed"
    resp_json = response.json()
    data = resp_json.get("data", {})
    file_id = data.get("id")
    assert file_id, "No file ID in response"
    
    yield data  # Provide file data to test
    
    # Cleanup
    delete_payload = {"file_id": file_id}
    delete_response = base_setup.post("/google-drive/delete_file", payload=delete_payload)
    assert delete_response.status_code == 200, "Failed to delete text file"

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

def test_list_files(base_setup, uploaded_url_file):
    """Test listing files with filters"""
    payload = {
        "filters": {
            "name_contains": "neon",
            "mime_type": "image/jpeg"
        }
    }
    response = base_setup.post("/google-drive/list_files", payload=payload)
    assert response.status_code == 200
    data = response.json().get("data", {})
    assert any(f["name"] == "neon_orb.webp" for f in data.get("files", []))

def test_get_file(base_setup, uploaded_url_file):
    """Test retrieving file metadata"""
    file_id = uploaded_url_file["id"]
    payload = {"file_id": file_id}
    response = base_setup.post("/google-drive/get_file", payload=payload)
    assert response.status_code == 200
    data = response.json().get("data", {})
    assert data["name"] == "neon_orb.webp"
    assert data["id"] == file_id

def test_create_and_delete_folder(base_setup):
    """Test folder lifecycle operations"""
    # Create folder
    create_payload = {
        "folder": {
            "name": "Test Folder"
        }
    }
    create_response = base_setup.post("/google-drive/create_folder", payload=create_payload)
    assert create_response.status_code == 200
    folder_data = create_response.json().get("data", {})
    
    # Verify folder creation
    assert folder_data["mime_type"] == "application/vnd.google-apps.folder"
    
    # Delete folder
    delete_payload = {"file_id": folder_data["id"]}
    delete_response = base_setup.post("/google-drive/delete_file", payload=delete_payload)
    assert delete_response.status_code == 200

def test_download_file(base_setup, uploaded_url_file):
    """Test file download with metadata"""
    file_id = uploaded_url_file["id"]
    payload = {"file_id": file_id}
    response = base_setup.post("/google-drive/download_file", payload=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "file_content" in data

def test_move_file(base_setup, uploaded_url_file):
    """Test moving a file between folders"""
    # Create a copy of the file for this test
    copy_payload = {
        "file_id": uploaded_url_file["id"]
    }
    copy_response = base_setup.post("/google-drive/copy_file", payload=copy_payload)
    assert copy_response.status_code == 200
    file_copy = copy_response.json().get("data", {})
    file_id = file_copy["id"]
    
    # Create target folder
    folder_payload = {
        "folder": {
            "name": "Target Folder"
        }
    }
    folder_response = base_setup.post("/google-drive/create_folder", payload=folder_payload)
    folder_id = folder_response.json().get("data", {}).get("id")
    
    # Move file copy
    move_payload = {
        "file_id": file_id,
        "new_parent_id": folder_id
    }
    move_response = base_setup.post("/google-drive/move_file", payload=move_payload)
    assert move_response.status_code == 200
    
    # Verify new parent
    get_response = base_setup.post("/google-drive/get_file", {"file_id": file_id})
    assert folder_id in get_response.json().get("data", {}).get("parent_ids", [])
    
    # Cleanup - delete both the copy and the folder
    base_setup.post("/google-drive/delete_file", {"file_id": file_id})
    base_setup.post("/google-drive/delete_file", {"file_id": folder_id})

def test_list_folders(base_setup):
    """Test listing folders specifically"""
    # Create test folder
    folder_payload = {
        "folder": {
            "name": "Test List Folder"
        }
    }
    create_response = base_setup.post("/google-drive/create_folder", payload=folder_payload)
    folder_id = create_response.json().get("data", {}).get("id")
    
    # List folders
    list_payload = {
        "filters": {
            "name_contains": "Test List"
        }
    }
    response = base_setup.post("/google-drive/list_folders", payload=list_payload)
    
    assert response.status_code == 200
    data = response.json().get("data", {})
    assert any(f["name"] == "Test List Folder" for f in data.get("files", []))
    
    # Cleanup
    base_setup.post("/google-drive/delete_file", {"file_id": folder_id})

def test_read_file_content(base_setup, uploaded_text_file):
    """Test reading file content"""
    payload = {"file_id": uploaded_text_file["id"]}
    response = base_setup.post("/google-drive/read_file", payload=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify success
    assert data["success"] is True, f"Failed to read file: {data.get('error', 'Unknown error')}"
    
    # Verify content exists and matches expected
    assert "content" in data
    assert "Hello, this is a test file!" in data["content"]
    
    # Verify file metadata
    assert data["file"]["name"] == "test.txt"
    assert data["mime_type"] == "text/plain"

def test_set_and_list_permissions(base_setup, uploaded_url_file):
    """Test setting and listing permissions"""
    file_id = uploaded_url_file["id"]
    
    # Set permission
    perm_payload = {
        "file_id": file_id,
        "permission": {
            "email": "test@example.com",
            "role": "reader",
            "type": "user"
        }
    }
    set_response = base_setup.post("/google-drive/set_permission", payload=perm_payload)
    assert set_response.status_code == 200
    
    # List permissions
    list_payload = {"file_id": file_id}
    list_response = base_setup.post("/google-drive/list_permissions", payload=list_payload)
    assert list_response.status_code == 200
    
    permissions = list_response.json().get("data", [])
    assert any(p["email_address"].lower() == "test@example.com" for p in permissions)

def test_delete_permission(base_setup, uploaded_url_file):
    """Test permission lifecycle"""
    file_id = uploaded_url_file["id"]
    
    # First set a permission
    perm_payload = {
        "file_id": file_id,
        "permission": {
            "email": "test@example.com",
            "role": "reader",
            "type": "user"
        }
    }

    set_response = base_setup.post("/google-drive/set_permission", payload=perm_payload)
    perm_id = set_response.json().get("data", {}).get("id")
    # Delete permission
    del_payload = {
        "file_id": file_id,
        "permission_id": perm_id
    }
    del_response = base_setup.post("/google-drive/delete_permission", payload=del_payload)
    assert del_response.status_code == 200
    
    # Verify deletion
    list_response = base_setup.post("/google-drive/list_permissions", {"file_id": file_id})
    permissions = list_response.json().get("data", [])
    assert not any(p["id"] == perm_id for p in permissions) 

def test_user_permission_lifecycle(base_setup, uploaded_url_file):
    """Test full lifecycle of user permissions"""
    file_id = uploaded_url_file["id"]
    
    # Set permission
    perm_payload = {
        "file_id": file_id,
        "permission": {
            "type": "user",
            "role": "writer",
            "email": "test@example.com"
        }
    }
    set_response = base_setup.post("/google-drive/set_permission", payload=perm_payload)
    assert set_response.status_code == 200, "User permission setting failed"
    
    # List permissions
    list_response = base_setup.post("/google-drive/list_permissions", {"file_id": file_id})
    permissions = list_response.json().get("data", [])
    user_perms = [p for p in permissions if p["type"] == "user"]
    assert any(p["email_address"].lower() == "test@example.com" for p in user_perms)
    
    # Cleanup
    perm_id = [p["id"] for p in user_perms if p["email_address"].lower() == "test@example.com"][0]
    del_response = base_setup.post("/google-drive/delete_permission", {
        "file_id": file_id,
        "permission_id": perm_id
    })
    assert del_response.status_code == 200, "User permission deletion failed"

def test_domain_permission(base_setup, uploaded_url_file):
    pass # we can't test domain cause we don't have a domain to test with
    # """Test domain permission setup"""
    # file_id = uploaded_url_file["id"]
    
    # perm_payload = {
    #     "file_id": file_id,
    #     "permission": {
    #         "type": "domain",
    #         "role": "commenter",
    #         "domain": "veyrax.com"
    #     }
    # }
    # response = base_setup.post("/google-drive/set_permission", payload=perm_payload)
    # assert response.status_code == 200, "Domain permission failed"
    
    # # Domain permissions might not appear in regular list, verify through API
    # list_response = base_setup.post("/google-drive/list_permissions", {"file_id": file_id})
    # assert response.status_code == 200

def test_public_link_permission(base_setup, uploaded_url_file):
    """Test creating public link permissions"""
    file_id = uploaded_url_file["id"]
    
    perm_payload = {
        "file_id": file_id,
        "permission": {
            "type": "anyone",
            "role": "reader"
        }
    }
    response = base_setup.post("/google-drive/set_permission", payload=perm_payload)
    assert response.status_code == 200, "Public link creation failed"
    
    # Verify public access
    list_response = base_setup.post("/google-drive/list_permissions", {"file_id": file_id})
    assert list_response.status_code == 200
    permissions = list_response.json().get("data", [])
    assert any(p["type"] == "anyone" for p in permissions)
