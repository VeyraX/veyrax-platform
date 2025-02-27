from aci_server.integrations.common.tests.base import base_setup
import pytest
from datetime import datetime

# Util for creating unique titles
def get_timestamped_title(base_title: str) -> str:
    """
    Adds a timestamp to a title to make it unique.
    
    Args:
        base_title (str): The base title to add timestamp to
        
    Returns:
        str: Title with timestamp appended
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_title} {timestamp}"

###########################################
# Fixtures
###########################################

@pytest.fixture(scope="module")
def test_titles():
    """
    Creates and stores timestamped titles for use across tests
    """
    return {
        "original": get_timestamped_title("Test Page Title"),
        "updated": get_timestamped_title("Updated Test Page Title")
    }

@pytest.fixture(scope="module")
def existing_space(base_setup):
    """
    This fixture retrieves the list of Confluence spaces,
    picks one to use in subsequent tests. 
    If no spaces are available, it will fail the tests.
    """
    response = base_setup.post("/confluence/spaces")
    assert response.status_code == 200, "Failed to retrieve spaces."
    resp_json = response.json()
    data = resp_json.get("data", {})
    spaces = data.get("spaces", [])
    
    # Ensure we have at least one space.
    assert len(spaces) > 0, "No spaces returned. Cannot proceed with tests."
    
    # For simplicity, pick the first space in the list.
    chosen_space = spaces[0]
    
    # The 'id' might be an integer or a string (depending on Confluence).
    # We'll just pass along the entire chosen_space or just the ID.
    return chosen_space


@pytest.fixture(scope="module")
def created_page(base_setup, existing_space, request, test_titles):
    """
    Creates a page in the first available space from existing_space.
    Yields the created page's ID for other tests.
    Cleanup is optional and controlled by 'auto_cleanup' marker.
    """
    space_id = existing_space["id"]
    
    create_payload = {
        "page": {
            "title": test_titles["original"],
            "content": f"<p>This is test page content for {test_titles['original']}.</p>",
            "spaceId": str(space_id)
        }
    }
    
    response = base_setup.post("/confluence/create_page", payload=create_payload)
    assert response.status_code == 200, "Failed to create page."
    resp_json = response.json()
    data = resp_json.get("data", {})
    
    page_id = data.get("id")
    assert page_id, "No page ID returned in create_page response."
    
    yield page_id
    
    # Only cleanup if test is marked with auto_cleanup
    if request.node.get_closest_marker('auto_cleanup'):
        try:
            delete_payload = {"page_id": page_id}
            base_setup.post("/confluence/delete_page", payload=delete_payload)
        except Exception:
            pass

###########################################
# Tests
###########################################

def test_list_spaces(base_setup):
    """
    Basic check to ensure /confluence/spaces returns some spaces.
    """
    response = base_setup.post("/confluence/spaces")
    assert response.status_code == 200, "Failed to list spaces."
    data = response.json().get("data", {})
    assert "spaces" in data, "Response data missing 'spaces' key."
    assert isinstance(data["spaces"], list), "'spaces' should be a list."
    # Optionally, ensure there's at least one space:
    assert len(data["spaces"]) > 0, "No spaces found."

def test_create_page(created_page):
    """
    Verifies that page creation (in the fixture) succeeded by checking the returned ID.
    """
    assert created_page, "Page was not created properly (missing ID)."

def test_get_page(base_setup, created_page):
    """
    Retrieves the newly created page and checks its ID.
    """
    payload = {"page_id": created_page}
    response = base_setup.post("/confluence/get_page", payload=payload)
    assert response.status_code == 200, "Failed to get page."
    
    resp_json = response.json()
    data = resp_json.get("data", {})
    assert data.get("id") == created_page, "Retrieved page ID does not match created page ID."

def test_update_page(base_setup, created_page, test_titles):
    """
    Updates the created page with a new title or content.
    """
    update_payload = {
        "page_id": created_page,
        "update": {
            "title": test_titles["updated"],
            "content": f"<p>Updated content for {test_titles['updated']}.</p>"
        }
    }
    response = base_setup.post("/confluence/update_page", payload=update_payload)
    assert response.status_code == 200, "Failed to update page."

def test_list_pages_contains_created(base_setup, created_page):
    """
    Calls /confluence/pages (list pages) to verify the newly created page is in the list.
    """
    list_payload = {
        "filters": {
            # You can optionally filter by space_id or partial title if your
            # API supports it. For demonstration, we'll just fetch all pages.
        }
    }
    response = base_setup.post("/confluence/pages", payload=list_payload)
    assert response.status_code == 200, "Failed to list pages."
    
    resp_json = response.json()
    data = resp_json.get("data", {})
    pages = data.get("pages", [])
    # Confirm the created page ID is present
    match = any(p.get("id") == created_page for p in pages)
    assert match, "Created page not found in the list of pages."

def test_search_content_for_page(base_setup, created_page, test_titles):
    """
    Uses /confluence/search to find the page by its updated title.
    """
    search_payload = {
        "title": test_titles["updated"]
    }
    response = base_setup.post("/confluence/search", payload=search_payload)
    assert response.status_code == 200, "Failed to search Confluence content."
    
    resp_json = response.json()
    data = resp_json.get("data", {})
    pages = data.get("pages", [])
    # Check if the updated page is returned in the search results
    match = any(p.get("id") == created_page for p in pages)
    assert match, "Updated page not found in search results."

def test_delete_page(base_setup, created_page):
    """
    Tests the delete_page endpoint by:
    1. Deleting a page
    2. Verifying the deletion response
    3. Attempting to get the deleted page to confirm it's gone
    """
    # First delete the page
    delete_payload = {"page_id": created_page}
    delete_response = base_setup.post("/confluence/delete_page", payload=delete_payload)
    assert delete_response.status_code == 200, "Failed to delete page"
    
    # Verify the response structure
    delete_json = delete_response.json()
    assert "data" in delete_json, "Response missing 'data' field"
    data = delete_json["data"]
    assert data["id"] == created_page, "Deleted page ID doesn't match"