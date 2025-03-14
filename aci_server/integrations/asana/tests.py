import pytest
import datetime
from integrations.common.tests.base import base_setup


TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
TEST_WORKSPACE_NAME = f"Test Workspace {TIMESTAMP}"
TEST_PROJECT_NAME = f"Test Project {TIMESTAMP}"
TEST_SECTION_NAME = f"Test Section {TIMESTAMP}"
TEST_TASK_NAME = f"Test Task {TIMESTAMP}"

@pytest.fixture(scope="module")
def workspace_data(base_setup):
    """
    Fixture that gets or creates a test workspace.
    We'll use this as our base for other tests.
    """
    response = base_setup.post("/asana/get_workspaces", payload={"limit": 1})
    assert response.status_code == 200, "Failed to get workspaces"
    
    data = response.json()
    workspaces = data.get("data", {}).get("items", [])
    
    if workspaces:
        return workspaces[0]
    else:
        pytest.skip("No workspace available for testing")

@pytest.fixture(scope="module")
def project_data(base_setup, workspace_data):
    create_project_payload = {
        "project": {
            "name": TEST_PROJECT_NAME,
            "workspace": workspace_data["gid"],
            "notes": "Test project for automated testing"
        }
    }
    
    response = base_setup.post("/asana/create_project", payload=create_project_payload)
    assert response.status_code == 200, "Failed to create test project"
    
    project = response.json().get("data")
    assert project["gid"], "No project ID in response"
    
    yield project
    
    archive_payload = {
        "project_id": project["gid"],
        "project_update": {"archived": True}
    }
    cleanup_response = base_setup.post("/asana/update_project", payload=archive_payload)
    assert cleanup_response.status_code == 200, "Failed to archive test project"

@pytest.fixture(scope="module")
def section_data(base_setup, project_data):
    create_section_payload = {
        "section": {
            "name": TEST_SECTION_NAME,
            "project": project_data["gid"]
        }
    }
    
    response = base_setup.post("/asana/create_section", payload=create_section_payload)
    assert response.status_code == 200, "Failed to create test section"
    
    section = response.json().get("data")
    assert section["gid"], "No section ID in response"
    
    return section

@pytest.fixture(scope="module")
def task_data(base_setup, project_data, section_data):
    create_task_payload = {
        "task": {
            "name": TEST_TASK_NAME,
            "notes": "Test task for automated testing",
            "projects": [project_data["gid"]],
            "workspace": project_data["workspace"]["gid"]
        }
    }
    
    response = base_setup.post("/asana/create_task", payload=create_task_payload)
    assert response.status_code == 200, "Failed to create test task"
    
    task = response.json().get("data")
    assert task["gid"], "No task ID in response"
    
    yield task
    
    delete_response = base_setup.post("/asana/delete_task", payload={"task_id": task["gid"]})
    assert delete_response.status_code == 200, "Failed to delete test task"

def test_get_workspaces(base_setup):
    response = base_setup.post("/asana/get_workspaces", payload={"limit": 10})
    assert response.status_code == 200, "Failed to get workspaces"
    data = response.json()
    assert "data" in data, "No data in response"
    assert "items" in data["data"], "No items in data"
    assert len(data["data"]["items"]) > 0, "No workspaces found"

def test_get_workspace(base_setup, workspace_data):
    response = base_setup.post("/asana/get_workspace", 
                             payload={"workspace_id": workspace_data["gid"]})
    assert response.status_code == 200, "Failed to get workspace"
    data = response.json()
    assert data["data"]["gid"] == workspace_data["gid"], "Workspace ID mismatch"

def test_get_projects(base_setup, workspace_data, project_data):
    response = base_setup.post("/asana/get_projects", 
                             payload={"workspace_id": workspace_data["gid"]})
    assert response.status_code == 200, "Failed to get projects"
    data = response.json()
    projects = data.get("data", [])
    assert any(p["gid"] == project_data["gid"] for p in projects), "Test project not found in list"

def test_get_project(base_setup, project_data):
    response = base_setup.post("/asana/get_project", 
                             payload={"project_id": project_data["gid"]})
    assert response.status_code == 200, "Failed to get project"
    data = response.json()
    assert data["data"]["gid"] == project_data["gid"], "Project ID mismatch"

def test_get_sections(base_setup, project_data, section_data):
    response = base_setup.post("/asana/get_sections", 
                             payload={"project_id": project_data["gid"]})
    assert response.status_code == 200, "Failed to get sections"
    data = response.json()
    sections = data["data"]["items"]
    assert any(s["gid"] == section_data["gid"] for s in sections), "Test section not found in list"

def test_get_section(base_setup, section_data):
    response = base_setup.post("/asana/get_section", 
                             payload={"section_id": section_data["gid"]})
    assert response.status_code == 200, "Failed to get section"
    data = response.json()
    assert data["data"]["gid"] == section_data["gid"], "Section ID mismatch"

def test_create_and_get_task(base_setup, project_data, task_data):
    response = base_setup.post("/asana/get_task", 
                             payload={"task_id": task_data["gid"]})
    assert response.status_code == 200, "Failed to get task"
    data = response.json()
    assert data["data"]["gid"] == task_data["gid"], "Task ID mismatch"
    assert data["data"]["name"] == TEST_TASK_NAME, "Task name mismatch"

def test_update_task(base_setup, task_data):
    update_payload = {
        "task_id": task_data["gid"],
        "task_update": {
            "name": f"Updated {TEST_TASK_NAME}",
            "notes": "Updated test task notes"
        }
    }
    
    response = base_setup.post("/asana/update_task", payload=update_payload)
    assert response.status_code == 200, "Failed to update task"
    data = response.json()
    assert data["data"]["name"] == f"Updated {TEST_TASK_NAME}", "Task name not updated"

def test_create_and_get_subtask(base_setup, task_data):
    create_subtask_payload = {
        "parent_task_id": task_data["gid"],
        "subtask": {
            "name": f"Subtask of {TEST_TASK_NAME}",
            "notes": "Test subtask for automated testing"
        }
    }
    
    response = base_setup.post("/asana/create_subtask", payload=create_subtask_payload)
    assert response.status_code == 200, "Failed to create subtask"
    subtask_data = response.json().get("data")
    
    response = base_setup.post("/asana/get_subtasks", 
                             payload={"task_id": task_data["gid"]})
    assert response.status_code == 200, "Failed to get subtasks"
    data = response.json()
    subtasks = data["data"]["items"]
    assert any(s["gid"] == subtask_data["gid"] for s in subtasks), "Subtask not found in list"
    
    delete_response = base_setup.post("/asana/delete_task", 
                                    payload={"task_id": subtask_data["gid"]})
    assert delete_response.status_code == 200, "Failed to delete subtask"

def test_get_section_tasks(base_setup, section_data, task_data):
    response = base_setup.post("/asana/get_section_tasks", 
                             payload={"section_id": section_data["gid"]})
    assert response.status_code == 200, "Failed to get section tasks"
    data = response.json()
    tasks = data["data"]["items"]
    assert any(t["gid"] == task_data["gid"] for t in tasks), "Test task not found in section"