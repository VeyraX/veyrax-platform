# TODO: dropbox tests can't be added because no integration token is available
 
# from aci_server.integrations.common.tests.base import base_setup
# import pytest
# import base64
# import os
# from datetime import datetime

# ###########################################
# # Utility functions
# ###########################################

# def get_timestamped_name(base_name: str) -> str:
#     """Add timestamp to a name to make it unique"""
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     return f"{base_name}_{timestamp}"

# def encode_file_content(content: str) -> str:
#     """Convert string content to base64 for file uploads"""
#     return base64.b64encode(content.encode('utf-8')).decode('utf-8')

# ###########################################
# # Fixtures
# ###########################################

# @pytest.fixture(scope="module")
# def test_names():
#     """Create unique names for test resources"""
#     return {
#         "folder": get_timestamped_name("test_folder"),
#         "file": get_timestamped_name("test_file.txt"),
#         "moved_file": get_timestamped_name("moved_file.txt")
#     }

# @pytest.fixture(scope="module")
# def test_folder(base_setup, test_names, request):
#     """
#     Creates a test folder in Dropbox root.
#     Yields the folder path.
#     Cleans up after tests if auto_cleanup marker is present.
#     """
#     folder_path = f"/{test_names['folder']}"
#     payload = {
#         "folder": {
#             "path": folder_path
#         }
#     }
    
#     response = base_setup.post("/dropbox/create_folder", payload=payload)
#     assert response.status_code == 200, f"Failed to create folder: {response.text}"
    
#     yield folder_path
    
#     # Clean up if auto_cleanup marker is present
#     if request.node.get_closest_marker('auto_cleanup'):
#         try:
#             # Check if folder exists first
#             get_response = base_setup.post("/dropbox/get_file", payload={"path": folder_path}, expected_status=None)
#             if get_response.status_code == 200:
#                 # Delete folder if it exists
#                 base_setup.post("/dropbox/delete_file", payload={"path": folder_path})
#         except Exception as e:
#             print(f"Error during cleanup: {e}")

# @pytest.fixture(scope="module")
# def test_file(base_setup, test_folder, test_names, request):
#     """
#     Creates a test file in the test folder.
#     Yields the file path.
#     """
#     file_path = f"{test_folder}/{test_names['file']}"
#     file_content = f"This is a test file content for {test_names['file']}"
    
#     payload = {
#         "path": file_path,
#         "file_content": encode_file_content(file_content),
#         "mode": "add"
#     }
    
#     response = base_setup.post("/dropbox/upload_file", payload=payload)
#     assert response.status_code == 200, f"Failed to upload file: {response.text}"
    
#     yield file_path
    
#     # No cleanup here as the folder cleanup will handle it

# @pytest.fixture(scope="module")
# def moved_file_path(test_folder, test_names):
#     """Returns the destination path for the moved file tests"""
#     return f"{test_folder}/{test_names['moved_file']}"

# ###########################################
# # Tests
# ###########################################

# def test_list_files_root(base_setup):
#     """Test listing files in the root directory"""
#     payload = {
#         "filters": {
#             "path": "",
#             "recursive": False,
#             "limit": 20
#         }
#     }
    
#     response = base_setup.post("/dropbox/list_files", payload=payload)
#     assert response.status_code == 200, "Failed to list files in root"
    
#     data = response.json().get("data", {})
#     assert "files" in data, "Response data missing 'files' key"
#     assert isinstance(data["files"], list), "'files' should be a list"

# def test_create_folder(test_folder):
#     """Test folder creation (indirectly tested via fixture)"""
#     assert test_folder, "Folder path should be returned from fixture"

# def test_upload_file(test_file):
#     """Test file upload (indirectly tested via fixture)"""
#     assert test_file, "File path should be returned from fixture"

# def test_get_file(base_setup, test_file):
#     """Test retrieving file metadata"""
#     payload = {"path": test_file}
    
#     response = base_setup.post("/dropbox/get_file", payload=payload)
#     assert response.status_code == 200, "Failed to get file metadata"
    
#     data = response.json().get("data", {})
#     assert data.get("path_display", "").lower() == test_file.lower(), "File path doesn't match expected value"
#     assert not data.get("is_folder", True), "File should not be identified as a folder"

# def test_list_files_folder(base_setup, test_folder, test_file):
#     """Test listing files in the test folder, confirming test file is included"""
#     payload = {
#         "filters": {
#             "path": test_folder,
#             "recursive": False,
#             "limit": 20
#         }
#     }
    
#     response = base_setup.post("/dropbox/list_files", payload=payload)
#     assert response.status_code == 200, "Failed to list files in test folder"
    
#     data = response.json().get("data", {})
#     files = data.get("files", [])
    
#     # Find our test file in the list
#     file_names = [file.get("name") for file in files]
#     file_name = os.path.basename(test_file)
#     assert file_name in file_names, f"Test file {file_name} not found in folder listing"

# def test_download_file(base_setup, test_file):
#     """Test downloading file content"""
#     payload = {"path": test_file}
    
#     response = base_setup.post("/dropbox/download_file", payload=payload)
#     assert response.status_code == 200, "Failed to download file"
    
#     data = response.json().get("data", {})
#     assert "file_content" in data, "Response missing file_content field"
#     assert "mime_type" in data, "Response missing mime_type field"
#     assert "filename" in data, "Response missing filename field"
    
#     # Decode and check content
#     decoded_content = base64.b64decode(data["file_content"]).decode('utf-8')
#     assert "This is a test file content" in decoded_content, "File content doesn't match expected value"

# def test_read_file(base_setup, test_file):
#     """Test reading file as text"""
#     payload = {"path": test_file}
    
#     response = base_setup.post("/dropbox/read_file", payload=payload)
#     assert response.status_code == 200, "Failed to read file"
    
#     result = response.json()
#     assert result.get("success", False), f"Read file operation failed: {result.get('error', 'Unknown error')}"
    
#     data = result.get("data", {})
#     assert "content" in data, "Response missing content field"
#     assert "This is a test file content" in data["content"], "File content doesn't match expected value"

# def test_move_file(base_setup, test_file, moved_file_path):
#     """Test moving a file to a new location"""
#     payload = {
#         "from_path": test_file,
#         "to_path": moved_file_path
#     }
    
#     response = base_setup.post("/dropbox/move_file", payload=payload)
#     assert response.status_code == 200, f"Failed to move file: {response.text}"
    
#     # Verify the file exists at the new location
#     get_payload = {"path": moved_file_path}
#     get_response = base_setup.post("/dropbox/get_file", payload=get_payload)
#     assert get_response.status_code == 200, "Failed to get moved file"
    
#     # Verify the file no longer exists at the old location
#     old_get_response = base_setup.post("/dropbox/get_file", payload={"path": test_file}, expected_status=None)
#     assert old_get_response.status_code != 200, "File still exists at original location after move"

# def test_delete_file(base_setup, moved_file_path):
#     """Test deleting a file"""
#     payload = {"path": moved_file_path}
    
#     response = base_setup.post("/dropbox/delete_file", payload=payload)
#     assert response.status_code == 200, "Failed to delete file"
    
#     # Verify the file no longer exists
#     get_response = base_setup.post("/dropbox/get_file", payload=payload, expected_status=None)
#     assert get_response.status_code != 200, "File still exists after deletion"

# @pytest.mark.auto_cleanup
# def test_delete_folder(base_setup, test_folder):
#     """Test deleting the test folder"""
#     payload = {"path": test_folder}
    
#     response = base_setup.post("/dropbox/delete_file", payload=payload)
#     assert response.status_code == 200, "Failed to delete folder"
    
#     # Verify the folder no longer exists
#     get_response = base_setup.post("/dropbox/get_file", payload=payload, expected_status=None)
#     assert get_response.status_code != 200, "Folder still exists after deletion" 