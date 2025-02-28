import pytest
from aci_server.integrations.common.tests.base import base_setup

# ------------------------------------------------------------------------------
# New helper fixtures for picking a valid project key and issue type
# ------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def test_project_id(base_setup):
    """
    Retrieves a list of Jira projects and returns the 'key' of the first one, 
    or skips the test if none are available.
    """
    response = base_setup.post("/jira/get_projects", payload={})
    assert response.status_code == 200, (
        f"Route /jira/get_projects failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    projects = response.json().get("data", [])
    if not projects:
        pytest.skip("No Jira projects found. Skipping the project tests.")
    # Pick the first project in the list (any valid project)
    first_project_key = projects[0].get("id")
    return first_project_key

@pytest.fixture(scope="module")
def test_issue_type_id(base_setup):
    """
    Retrieves a list of Jira issue types and returns the 'id' of a standard issue type,
    avoiding sub-tasks which require parent issues.
    """
    response = base_setup.post("/jira/get_issue_types", payload={})
    assert response.status_code == 200, (
        f"Route /jira/get_issue_types failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    issue_types = response.json().get("data", [])
    if not issue_types:
        pytest.skip("No Jira issue types found. Skipping the issue creation tests.")
    
    # Filter out sub-task issue types to avoid the parent requirement
    standard_issue_types = [it for it in issue_types if it.get('name', '').lower() == 'task']
    
    return standard_issue_types[0].get("id")

# ------------------------------------------------------------------------------
# Fixtures for creating and cleaning up an issue
# ------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def issue_payload(test_project_id, test_issue_type_id):
    """
    Provides a minimal valid payload for creating a Jira issue, using
    the discovered project key and issue type ID.
    """
    # Use a timestamp to ensure unique summary for each test run
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "issue_args": {
            "project_id": test_project_id,
            "summary": f"Test Issue from PyTest {timestamp}",
            "issue_type_id": test_issue_type_id,
            "description": "This is a test issue created by the automated test suite.",
            # Optional fields below - uncomment if needed for specific tests
            # "labels": ["test", "automation"],
            # "components": ["API"]
        }
    }

@pytest.fixture(scope="module")
def created_issue(base_setup, issue_payload):
    """
    Creates an issue using the provided payload. Yields the newly created issue key.
    Cleans up (deletes) the issue afterward if still present.
    """

    # Try to create the issue
    create_response = base_setup.post("/jira/create_issue", payload=issue_payload)
    
    # If creation fails with a subtask error, try to get a parent issue or skip
    if create_response.status_code != 200 and "subtask" in create_response.text.lower() and "parent" in create_response.text.lower():
        
        # Try to get an existing issue to use as parent
        get_issues_response = base_setup.post("/jira/get_issues", 
                                             payload={"filters": {"project_id": issue_payload["issue_args"]["project_id"], "max_results": 1}})
        
        if get_issues_response.status_code == 200:
            issues = get_issues_response.json().get("data", {}).get("issues", [])
            if issues:
                parent_key = issues[0].get("key")
                
                # Update payload with parent issue
                issue_payload["issue_args"]["parent_issue_key"] = parent_key
                create_response = base_setup.post("/jira/create_issue", payload=issue_payload)
            else:
                pytest.skip("No parent issues available for subtask creation")
    
    # Verify creation was successful
    assert create_response.status_code == 200, (
        f"Route /jira/create_issue failed. "
        f"Expected 200, got {create_response.status_code}. Response: {create_response.text}"
    )
    
    created_data = create_response.json().get("data", {})
    issue_key = created_data.get("key")
    assert issue_key, "No issue key returned in create_issue response."
    
    
    # Yield the issue key for test use
    yield issue_key

    try:
        base_setup.post("/jira/delete_issue", payload={"issue_id": issue_key})
    except Exception as e:
        print(f"Warning: Failed to delete test issue {issue_key}: {str(e)}")

# ------------------------------------------------------------------------------
# Tests for Projects, Statuses, Priorities, Issue Types, Fields, and Users
# ------------------------------------------------------------------------------

def test_get_projects(base_setup):
    """
    Tests the /jira/get_projects endpoint to ensure it responds with a list of projects.
    """
    response = base_setup.post("/jira/get_projects", payload={})
    assert response.status_code == 200, (
        f"Route /jira/get_projects failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json().get("data", [])
    assert isinstance(data, list), "Expected a list of projects in response."

def test_get_project(base_setup, test_project_id):
    """
    Tests the /jira/get_project endpoint by retrieving a known, valid project.
    If the discovered project doesn't exist (edge case), we skip.
    """
    payload = {"project_id": test_project_id}
    response = base_setup.post("/jira/get_project", payload=payload)
    if response.status_code == 404:
        pytest.skip(f"Project '{test_project_id}' not found. Skipping test.")
    assert response.status_code == 200, (
        f"Route /jira/get_project failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json().get("data", {})
    assert data.get("id"), "No 'id' found in project data."

def test_get_statuses(base_setup):
    """
    Tests the /jira/get_statuses endpoint to ensure it returns available statuses.
    """
    response = base_setup.post("/jira/get_statuses", payload={})
    assert response.status_code == 200, (
        f"Route /jira/get_statuses failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json().get("data", [])
    assert isinstance(data, list), "Expected a list of statuses in response."

def test_get_priorities(base_setup):
    """
    Tests the /jira/get_priorities endpoint to ensure it returns available priorities.
    """
    response = base_setup.post("/jira/get_priorities", payload={})
    assert response.status_code == 200, (
        f"Route /jira/get_priorities failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json().get("data", [])
    assert isinstance(data, list), "Expected a list of priorities in response."

def test_get_issue_types(base_setup):
    """
    Tests the /jira/get_issue_types endpoint to ensure it returns available issue types.
    """
    response = base_setup.post("/jira/get_issue_types", payload={})
    assert response.status_code == 200, (
        f"Route /jira/get_issue_types failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json().get("data", [])
    assert isinstance(data, list), "Expected a list of issue types in response."

def test_get_fields(base_setup):
    """
    Tests the /jira/get_fields endpoint to ensure it returns available fields.
    """
    response = base_setup.post("/jira/get_fields", payload={})
    assert response.status_code == 200, (
        f"Route /jira/get_fields failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json().get("data", [])
    assert isinstance(data, list), "Expected a list of fields in response."

def test_get_users(base_setup):
    """
    Tests the /jira/get_users endpoint to verify user search functionality.
    Query can be left empty or adapted to your environment.
    """
    payload = {"query": ""}
    response = base_setup.post("/jira/get_users", payload=payload)
    assert response.status_code == 200, (
        f"Route /jira/get_users failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json().get("data", [])
    assert isinstance(data, list), "Expected a list of users in response."

# ------------------------------------------------------------------------------
# Tests for the full Issue Lifecycle: create → update → get → list → delete
# ------------------------------------------------------------------------------

def test_create_issue(created_issue):
    """
    Verifies that the issue creation (in the fixture) succeeded by checking we have a valid issue key.
    """
    assert created_issue, "Issue creation fixture failed to provide a valid issue key."

def test_get_issue(base_setup, created_issue):
    """
    Attempts to retrieve the created issue by issue key and checks for matching key.
    """
    payload = {"issue_id": created_issue}
    response = base_setup.post("/jira/get_issue", payload=payload, expected_status=None)
    # If the route or the environment is misconfigured, it might return 404 or 400, but we expect 200 for success.
    assert response.status_code == 200, (
        f"Route /jira/get_issue failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json().get("data", {})
    assert data.get("key") == created_issue, "Retrieved issue key does not match created issue key."

def test_update_issue(base_setup, created_issue):
    """
    Updates the created issue with a new summary or other fields.
    """
    payload = {
        "issue_id": created_issue,
        "update_args": {
            "summary": "Updated Test Issue Summary via PyTest",
            "description": "This is an updated description."
        }
    }
    response = base_setup.post("/jira/update_issue", payload=payload, expected_status=None)
    assert response.status_code == 200, (
        f"Route /jira/update_issue failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    # Optionally, retrieve the updated issue to confirm changes:
    get_resp = base_setup.post("/jira/get_issue", payload={"issue_id": created_issue})
    updated_data = get_resp.json().get("data", {})
    assert updated_data.get("summary") == "Updated Test Issue Summary via PyTest", "Issue summary was not updated."

def test_list_issues(base_setup, created_issue, test_project_id):
    """
    Calls /jira/get_issues to verify the newly created (and updated) issue is in the list.
    Uses the discovered project key from test_project_id.
    """
    payload = {
        "filters": {
            "project_id": test_project_id
        }
    }
    response = base_setup.post("/jira/get_issues", payload=payload, expected_status=None)
    assert response.status_code == 200, (
        f"Route /jira/get_issues failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    issues = response.json().get("data", {}).get("issues", [])
    # Look for the created_issue key in the list of issues.
    match = any(issue.get("key") == created_issue for issue in issues)
    assert match, "Created issue not found in the list of Jira issues."

def test_delete_issue(base_setup, created_issue):
    """
    Deletes the created issue. This test won't run if earlier tests fail 
    because the 'created_issue' fixture won't be set.
    """
    delete_payload = {"issue_id": created_issue}
    del_response = base_setup.post("/jira/delete_issue", payload=delete_payload, expected_status=None)
    assert del_response.status_code == 200, (
        f"Route /jira/delete_issue failed. "
        f"Expected 200, got {del_response.status_code}. Response: {del_response.text}"
    )

    # Verify the issue is actually deleted by trying to fetch it again.
    get_response = base_setup.post("/jira/get_issue", payload={"issue_id": created_issue}, expected_status=None)
    # We expect 404 or similar for a deleted issue, definitely not 200.
    assert get_response.status_code != 200, "Issue still exists after deletion." 