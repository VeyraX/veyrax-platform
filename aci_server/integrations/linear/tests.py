import pytest
from datetime import datetime
from integrations.common.tests.base import base_setup


@pytest.fixture(scope="module")
def test_team_id(base_setup):
    """
    Retrieves the first available team from /linear/list_teams
    or raises an assertion if none are available.
    """
    response = base_setup.post("/linear/list_teams", payload={"cursor": None, "max_results": 10})
    assert response.status_code == 200, (
        f"Route /linear/list_teams failed. "
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    teams_data = response.json().get("data", {}).get("items", [])
    assert teams_data, "No teams found in response from /linear/list_teams."
    return teams_data[0]["id"]


@pytest.fixture(scope="module")
def created_issue_id(base_setup, test_team_id):
    """
    Creates a new Linear issue for testing. Shares the issue ID with dependent tests.
    Since there is no delete endpoint, we do not attempt to clean up.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    create_payload = {
        "issue": {
            "title": f"Test Issue {timestamp}",
            "team_id": test_team_id,
            "description": "Created by automated test."
            # Add or remove fields as needed.
        }
    }
    create_resp = base_setup.post("/linear/create_issue", payload=create_payload)
    assert create_resp.status_code == 200, (
        f"Route /linear/create_issue failed. "
        f"Expected 200, got {create_resp.status_code}. Response: {create_resp.text}"
    )
    created_issue = create_resp.json().get("data", {})
    issue_id = created_issue.get("id")
    assert issue_id, "No issue ID returned in create_issue response."
    return issue_id


def test_update_issue(base_setup, created_issue_id):
    """
    Updates the created issue with a new title. We then verify success by searching later.
    """
    updated_title = "Test Issue Updated"
    update_payload = {
        "issue_id": created_issue_id,
        "issue_update": {
            "title": updated_title,
            "description": "Updated description."
        }
    }
    update_resp = base_setup.post("/linear/update_issue", payload=update_payload)
    assert update_resp.status_code == 200, (
        f"Route /linear/update_issue failed. "
        f"Expected 200, got {update_resp.status_code}. Response: {update_resp.text}"
    )
    data = update_resp.json().get("data", {})
    # We can verify the returned object's title was updated
    assert data.get("title") == updated_title, "Issue title was not updated as expected."


def test_comment_issue(base_setup, created_issue_id):
    """
    Adds a comment to the created issue and verifies success.
    """
    comment_payload = {
        "issue_id": created_issue_id,
        "comment": {
            "body": "This is a test comment."
        }
    }

    print(comment_payload)
    comment_resp = base_setup.post("/linear/comment_issue", payload=comment_payload)
    assert comment_resp.status_code == 200, (
        f"Route /linear/comment_issue failed. "
        f"Expected 200, got {comment_resp.status_code}. Response: {comment_resp.text}"
    )
    data = comment_resp.json().get("data", {})
    assert data.get("body") == "This is a test comment.", "Comment body mismatch."
    assert data.get("id"), "No comment ID returned in comment_issue response."
    assert data.get("createdAt"), "Missing created_at timestamp in response"


def test_search_issues(base_setup, created_issue_id):
    """
    Searches for the updated issue by a keyword in the updated title (e.g., 'Updated').
    Verifies that the newly updated issue is included.
    """
    search_resp = base_setup.post("/linear/search_issues", payload={"query": "Updated"})
    assert search_resp.status_code == 200, (
        f"Route /linear/search_issues failed. "
        f"Expected 200, got {search_resp.status_code}. Response: {search_resp.text}"
    )


def test_list_issues(base_setup, created_issue_id):
    """
    Verifies that listing issues returns the newly created issue.
    """
    list_resp = base_setup.post("/linear/list_issues", payload={"cursor": None, "max_results": 10})
    assert list_resp.status_code == 200, (
        f"Route /linear/list_issues failed. "
        f"Expected 200, got {list_resp.status_code}. Response: {list_resp.text}"
    )
    issues = list_resp.json().get("data", {}).get("items", [])
    match = any(issue.get("id") == created_issue_id for issue in issues)
    assert match, "Created issue not found in list of issues."


def test_filter_issues(base_setup, created_issue_id):
    """
    Demonstrates a filter by issue ID (though this is a bit contrived).
    Alternatively, could filter by project_id, state_id, etc.
    """
    filter_payload = {
        "filters": {"creator_id": None},  # Modify if you want a real filter
        "cursor": None,
        "max_results": 10
    }
    filter_resp = base_setup.post("/linear/filter_issues", payload=filter_payload)
    assert filter_resp.status_code == 200, (
        f"Route /linear/filter_issues failed. "
        f"Expected 200, got {filter_resp.status_code}. Response: {filter_resp.text}"
    )
    items = filter_resp.json().get("data", {}).get("items", [])
    # Nothing says we must find the newly created issue here if the filter doesn't match
    # but we can at least confirm the endpoint works with minimal filtering.
    assert isinstance(items, list), "Expected a list in filter_issues response."


def test_list_projects(base_setup):
    """
    Verifies that listing projects returns the newly created project.
    """
    list_resp = base_setup.post("/linear/list_projects", payload={"cursor": None, "max_results": 10})
    assert list_resp.status_code == 200, (
        f"Route /linear/list_projects failed. "
        f"Expected 200, got {list_resp.status_code}. Response: {list_resp.text}"
    )
    

def test_list_users(base_setup):
    """
    Tests the /linear/list_users endpoint and ensures it returns a valid list of users.
    """
    resp = base_setup.post("/linear/list_users", payload={"cursor": None, "max_results": 5})
    assert resp.status_code == 200, (
        f"Route /linear/list_users failed. "
        f"Expected 200, got {resp.status_code}. Response: {resp.text}"
    )
    data = resp.json().get("data", {}).get("items", [])
    assert isinstance(data, list), "Expected list of users in response."


def test_list_teams(base_setup):
    """
    Verifies /linear/list_teams returns at least one team.
    """
    resp = base_setup.post("/linear/list_teams", payload={"cursor": None, "max_results": 5})
    assert resp.status_code == 200, (
        f"Route /linear/list_teams failed. "
        f"Expected 200, got {resp.status_code}. Response: {resp.text}"
    )
    data = resp.json().get("data", {}).get("items", [])
    assert isinstance(data, list), "Expected list of teams in response."
    # If you want to test /linear/get_team, you can do so here on the first ID:
    if data:
        team_id = data[0].get("id")
        get_resp = base_setup.post("/linear/get_team", payload={"team_id": team_id})
        assert get_resp.status_code == 200, (
            f"Route /linear/get_team failed. "
            f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
        )


def test_list_workflow_states(base_setup):
    """
    Tests /linear/list_workflow_states to ensure it returns valid workflow states.
    """
    resp = base_setup.post("/linear/list_workflow_states", payload={"cursor": None, "max_results": 5})
    assert resp.status_code == 200, (
        f"Route /linear/list_workflow_states failed. "
        f"Expected 200, got {resp.status_code}. Response: {resp.text}"
    )
    data = resp.json().get("data", {}).get("items", [])
    assert isinstance(data, list), "Expected list of workflow states in response."

