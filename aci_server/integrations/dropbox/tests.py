import pytest
import base64
import datetime
from aci_server.integrations.common.tests.base import base_setup

# NEW: define timestamp-based variables here
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
TEST_FOLDER = f"/test_folder_{TIMESTAMP}"
TEST_FILE_NAME = f"test_file_{TIMESTAMP}.txt"
TEST_FILE_PATH = f"{TEST_FOLDER}/{TEST_FILE_NAME}"

# Example fixture that creates and eventually cleans up a test file in Dropbox.
@pytest.fixture(scope="function")
def dropbox_test_file(base_setup):
    """
    Fixture that uploads a small text file into Dropbox, 
    then deletes it after the test finishes.
    """
    # Base64-encoded content representing "Hello, dropbox!"
    text_b64 = base64.b64encode(b"Hello, dropbox!").decode("utf-8")
    upload_payload = {
        "path": TEST_FILE_PATH,
        "file_content": text_b64,
        "mode": "add"
    }
    upload_response = base_setup.post("/dropbox/upload_file", payload=upload_payload)
    assert upload_response.status_code == 200, "Dropbox test file upload failed"
    resp_data = upload_response.json()
    file_data = resp_data.get("data", {})
    file_id = file_data.get("id")
    file_name = file_data.get("name")
    assert file_id and file_name, "Upload did not return expected file info."

    yield file_data  # Provide the file data to the test

    # Cleanup: attempt to delete the file
    delete_payload = {"path": f"{TEST_FOLDER}/{file_name}"}
    delete_response = base_setup.post("/dropbox/delete_file", payload=delete_payload)
    assert delete_response.status_code == 200, "Failed to delete test file from Dropbox"

def test_list_files(base_setup, dropbox_test_file):
    """
    Test listing files with filters. 
    At minimum, we can check if the test file can be found in its folder.
    """
    list_payload = {
        "filters": {
            "path": TEST_FOLDER,
            "recursive": False,
            "limit": 20
        }
    }
    response = base_setup.post("/dropbox/list_files", payload=list_payload)
    assert response.status_code == 200, "Listing files failed"
    data = response.json().get("data", {})
    files = data.get("files", [])
    assert any(f["name"] == dropbox_test_file["name"] for f in files), \
        "Uploaded test file not found in list_files response"

def test_get_file(base_setup, dropbox_test_file):
    """
    Test retrieving file metadata via /dropbox/get_file
    """
    file_name = dropbox_test_file["name"]
    get_payload = {"path": f"{TEST_FOLDER}/{file_name}"}
    response = base_setup.post("/dropbox/get_file", payload=get_payload)
    assert response.status_code == 200, "Retrieving file metadata failed"
    data = response.json().get("data", {})
    assert data["name"] == file_name, "Fetched file name does not match"

def test_create_and_delete_folder(base_setup):
    """
    Test creating and deleting a folder in Dropbox
    """
    folder_path = f"/test_folder_for_deletion_{TIMESTAMP}"
    create_payload = {
        "folder": {"path": folder_path}
    }
    create_response = base_setup.post("/dropbox/create_folder", payload=create_payload)
    assert create_response.status_code == 200, "Failed to create folder in Dropbox"
    folder_data = create_response.json().get("data", {})
    assert folder_data.get("is_folder") is True, "Created item is not recognized as a folder"

    # Now delete the folder
    delete_payload = {"path": folder_path}
    delete_response = base_setup.post("/dropbox/delete_file", payload=delete_payload)
    assert delete_response.status_code == 200, "Failed to delete folder in Dropbox"

def test_download_file(base_setup, dropbox_test_file):
    """
    Test downloading a file from Dropbox
    """
    file_name = dropbox_test_file["name"]
    payload = {"path": f"{TEST_FOLDER}/{file_name}"}
    download_response = base_setup.post("/dropbox/download_file", payload=payload)
    assert download_response.status_code == 200, "Failed to download file"
    data = download_response.json()
    # We expect something like {"status": "success", "data": {...}}
    assert "data" in data, "No file data in download response"
    file_content = data["data"].get("file_content")
    assert file_content, "No file_content found in download response"
    # Optionally decode and check
    decoded_content = base64.b64decode(file_content).decode("utf-8")
    assert "Hello, dropbox!" in decoded_content, "Downloaded content is incorrect"

def test_move_file(base_setup, dropbox_test_file):
    """
    Test moving a file to a new path in Dropbox
    """
    file_path = f"{TEST_FOLDER}/{dropbox_test_file['name']}"
    new_folder_path = f"/test_folder_move_{TIMESTAMP}"
    # Create the target folder first
    create_folder_payload = {"folder": {"path": new_folder_path}}
    create_folder_resp = base_setup.post("/dropbox/create_folder", payload=create_folder_payload)
    assert create_folder_resp.status_code == 200, "Failed to create move target folder"

    move_payload = {
        "from_path": file_path,
        "to_path": f"{new_folder_path}/{dropbox_test_file['name']}"
    }
    move_response = base_setup.post("/dropbox/move_file", payload=move_payload)
    assert move_response.status_code == 200, "Failed to move file in Dropbox"

    #moving file back to original path
    move_payload = {
        "from_path": f"{new_folder_path}/{dropbox_test_file['name']}",
        "to_path": file_path
    }
    move_response = base_setup.post("/dropbox/move_file", payload=move_payload)
    assert move_response.status_code == 200, "Failed to move file in Dropbox"

    # Delete the folder, too
    delete_folder_resp = base_setup.post("/dropbox/delete_file", payload={"path": new_folder_path})
    assert delete_folder_resp.status_code == 200, "Failed to delete the new folder"

def test_read_file_content(base_setup, dropbox_test_file):
    """
    Test reading textual file content from Dropbox
    """
    file_path = f"{TEST_FOLDER}/{dropbox_test_file['name']}"
    payload = {"path": file_path}
    response = base_setup.post("/dropbox/read_file", payload=payload)
    assert response.status_code == 200, "Failed to read file content"
    data = response.json()
    assert data["success"] is True, f"Reading file content failed: {data.get('error', 'Unknown error')}"
    content = data["data"].get("content", "")
    assert "Hello, dropbox!" in content, "File content does not match expected text"

def test_create_shared_link(base_setup, dropbox_test_file):
    """
    Test creating a shared link for a file in Dropbox
    """
    file_path = f"{TEST_FOLDER}/{dropbox_test_file['name']}"
    payload = {"path": file_path}
    response = base_setup.post("/dropbox/create_shared_link", payload=payload)
    assert response.status_code == 200, "Failed to create shared link"

def test_search_files(base_setup, dropbox_test_file):
    """
    Test searching for files in Dropbox
    """
    # Search for the test file by name
    file_name = dropbox_test_file["name"]
    search_payload = {
        "query": file_name,
        "filename_only": True  # Only search in filenames
    }
    
    response = base_setup.post("/dropbox/search", payload=search_payload)
    assert response.status_code == 200, "Search request failed"
    
    # Verify we get a valid response structure
    data = response.json()
    assert "data" in data, "No data in search response"
    assert "files" in data["data"], "No files in search response" 