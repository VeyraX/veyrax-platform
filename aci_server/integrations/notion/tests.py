from integrations.common.tests.base import base_setup
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

def get_workspace_parent():
    return {
        "type": "workspace",
        "workspace": True
    }

@pytest.fixture
def existing_page_id(base_setup):
    """Fixture that provides a valid page ID from search results"""
    search_result = base_setup.post("/notion/search", payload={})
    assert search_result.status_code == 200, "Search request failed"
    items = search_result.json().get('data', {}).get('items', [])
    assert items, "No pages found in search results"
    return items[0]['id']

def test_search(base_setup):
    """
    Verifies that listing projects returns the newly created project.
    """
    search_result = base_setup.post("/notion/search", payload={})
    assert search_result.status_code == 200
    data = search_result.json().get('data', {})
    assert 'items' in data, "Search response missing 'items' field"
    assert len(data['items']) > 0, "No items found in search results"

def test_get_page(base_setup):
    """Test getting a single page"""
    # First search to get a page ID
    search_result = base_setup.post("/notion/search", payload={})
    if search_result.json().get('data', {}).get('items'):
        page_id = search_result.json()['data']['items'][0]['id']
        result = base_setup.post("/notion/get_page", payload={"page_id": page_id})
        assert result.status_code == 200

@pytest.fixture
def created_page_id(base_setup, existing_page_id):
    """Fixture that creates a new page and returns its ID for update tests"""
    new_page = {
        "parent": {
            "type": "page_id",
            "page_id": existing_page_id
        },
        "properties": {
            "title": {
                "title": [{"text": {"content": get_timestamped_title("Update Test Page")}}]
            }
        }
    }
    create_result = base_setup.post("/notion/create_page", payload={"page": new_page})
    assert create_result.status_code == 200, "Page creation failed in fixture"
    return create_result.json()['data']['items'][0]['id']

def test_create_page(base_setup, existing_page_id):
    """Test creating a page"""
    new_page = {
        "parent": {
            "type": "page_id",
            "page_id": existing_page_id
        },
        "properties": {
            "title": {
                "title": [{"text": {"content": get_timestamped_title("Test Page")}}]
            }
        }
    }   
    create_result = base_setup.post("/notion/create_page", payload={"page": new_page})
    
    assert create_result.status_code == 200

def test_update_page(base_setup, created_page_id):
    """Test updating a page"""
    update_data = {
        "page_id": created_page_id,
        "page_update": {
            "properties": {
                "title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Akbar Page Title"
                            }
                        }
                    ]
                }
            }
        }
    }
    update_result = base_setup.post("/notion/update_page", payload=update_data)
    
    assert update_result.status_code == 200

def test_list_databases(base_setup):
    """Test listing databases from Notion"""
    list_result = base_setup.post("/notion/list_databases", payload={})
    assert list_result.status_code == 200
    data = list_result.json().get('data', {})
    assert 'items' in data, "Response missing 'items' field"
    assert isinstance(data['items'], list), "Items should be a list"
    
    if data['items']:
        db = data['items'][0]
        assert 'id' in db, "Database missing ID"
        assert 'title' in db, "Database missing title"

def test_get_database(base_setup):
    """Test getting a single database"""
    # First get a database ID from list
    list_result = base_setup.post("/notion/list_databases", payload={})
    assert list_result.status_code == 200
    items = list_result.json().get('data', {}).get('items', [])
    
    if items:
        db_id = items[0]['id']
        get_result = base_setup.post("/notion/get_database", payload={"database_id": db_id})
        assert get_result.status_code == 200
        db_data = get_result.json().get('data', {})
        assert db_data['id'] == db_id, "Returned database ID mismatch"
        assert 'properties' in db_data, "Database missing properties"

def test_list_database_pages(base_setup):
    """Test listing pages in a database"""
    # Get a database ID
    list_db_result = base_setup.post("/notion/list_databases", payload={})
    assert list_db_result.status_code == 200
    databases = list_db_result.json().get('data', {}).get('items', [])
    
    if databases:
        db_id = databases[0]['id']
        list_pages_result = base_setup.post("/notion/list_database_pages", payload={
            "database_id": db_id
        })
        assert list_pages_result.status_code == 200
        pages_data = list_pages_result.json().get('data', {})
        assert 'items' in pages_data, "Response missing pages items"
        
        if pages_data['items']:
            page = pages_data['items'][0]
            assert 'id' in page, "Page missing ID"
            assert 'title' in page, "Page missing title"

def test_query_database(base_setup):
    """Test querying a database"""
    # Get a database ID
    list_db_result = base_setup.post("/notion/list_databases", payload={})
    assert list_db_result.status_code == 200
    databases = list_db_result.json().get('data', {}).get('items', [])
    
    if databases:
        db_id = databases[0]['id']
        query_result = base_setup.post("/notion/query_database", payload={
            "database_id": db_id
        })
        assert query_result.status_code == 200
        query_data = query_result.json().get('data', {})
        assert 'items' in query_data, "Response missing query items"
        assert isinstance(query_data['items'], list), "Items should be a list"
        
        if query_data['items']:
            page = query_data['items'][0]
            assert 'id' in page, "Page missing ID"
            assert 'title' in page, "Page missing title"

