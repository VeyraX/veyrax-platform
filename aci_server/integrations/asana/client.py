import requests
from typing import Optional, Dict, Any

class AsanaClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://app.asana.com/api/1.0"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )
        
        response.raise_for_status()
        return response.json()

    # Task operations
    def get_tasks(self, workspace_id: str, project_id: Optional[str] = None, 
                  assignee: Optional[str] = None, completed_since: Optional[str] = None, 
                  limit: int = 20, offset: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "limit": limit,
            "opt_fields": (
                "gid,name,completed,due_on,notes,"
                "assignee,assignee.gid,assignee.name,assignee.email,"
                "workspace,workspace.gid,workspace.name,"
                "projects,projects.gid,projects.name,"
                "parent,parent.gid,parent.name,"
                "created_at,modified_at"
            )
        }
        
        if project_id:
            params["project"] = project_id
        if workspace_id and not project_id:
            params["workspace"] = workspace_id
        if assignee:
            params["assignee"] = assignee
        if completed_since:
            params["completed_since"] = completed_since
        if offset:
            params["offset"] = offset
        
        return self._make_request("GET", "tasks", params=params)

    def get_task(self, task_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"tasks/{task_id}")

    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "tasks", data={"data": data})

    def update_task(self, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", f"tasks/{task_id}", data={"data": data})

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"tasks/{task_id}")

    # Subtask operations
    def get_subtasks(self, task_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"tasks/{task_id}/subtasks")

    def create_subtask(self, parent_task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        data["parent"] = parent_task_id
        return self._make_request("POST", "tasks", data={"data": data})
    
    # Workspace operations
    def get_workspaces(self, limit: int = 20, offset: Optional[str] = None) -> Dict[str, Any]:
        params = {"limit": limit}
        
        if offset:
            params["offset"] = offset
            
        return self._make_request("GET", "workspaces", params=params)

    def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"workspaces/{workspace_id}")

    # Project operations
    def get_projects(self, workspace_id: Optional[str] = None, team_id: Optional[str] = None, 
                    archived: Optional[bool] = None, limit: int = 20, 
                    offset: Optional[str] = None) -> Dict[str, Any]:
        params = {"limit": limit}
        
        if workspace_id:
            params["workspace"] = workspace_id
        if team_id:
            params["team"] = team_id
        if archived is not None:
            params["archived"] = str(archived).lower()
        if offset:
            params["offset"] = offset
            
        return self._make_request("GET", "projects", params=params)

    def get_project(self, project_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"projects/{project_id}")

    # Goal operations
    def get_goals(self, workspace_id: str, time_period_id: Optional[str] = None, 
                 owner_id: Optional[str] = None, is_workspace_level: Optional[bool] = None,
                 limit: int = 20, offset: Optional[str] = None) -> Dict[str, Any]:
        params = {"limit": limit}
        
        if workspace_id:
            params["workspace"] = workspace_id
        if time_period_id:
            params["time_period"] = time_period_id
        if owner_id:
            params["owner"] = owner_id
        if is_workspace_level is not None:
            params["is_workspace_level"] = str(is_workspace_level).lower()
        if offset:
            params["offset"] = offset
            
        return self._make_request("GET", "goals", params=params)

    def get_goal(self, goal_id: str) -> Dict[str, Any]:
        params = {
            "opt_fields": (
                "gid,name,due_on,notes,status,"
                "owner,owner.gid,owner.name,owner.email,"
                "workspace,workspace.gid,workspace.name,"
                "time_period,time_period.gid,time_period.name,"
                "metric,metric.gid,metric.name,metric.precision,metric.unit,"
                "metric.current_number_value,metric.target_number_value,"
                "is_workspace_level,liked"
            )
        }
        return self._make_request("GET", f"goals/{goal_id}", params=params)

    def create_goal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "goals", data={"data": data})

    def update_goal(self, goal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", f"goals/{goal_id}", data={"data": data})

    def get_tags(self, workspace_id: Optional[str] = None, project_id: Optional[str] = None, 
                 limit: int = 20, offset: Optional[str] = None) -> Dict[str, Any]:
        params = {"limit": limit}
        
        if workspace_id:
            params["workspace"] = workspace_id
        if project_id:
            params["project"] = project_id
        if offset:
            params["offset"] = offset
            
        return self._make_request("GET", "tags", params=params)

    def get_tag(self, tag_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"tags/{tag_id}")

    # Team operations
    def get_teams(self, workspace_id: str, limit: int = 20, 
                 offset: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "workspace": workspace_id,
            "limit": limit
        }
        
        if offset:
            params["offset"] = offset
            
        return self._make_request("GET", "teams", params=params)

    def get_team(self, team_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"teams/{team_id}")

    # User operations
    def get_users(self, workspace_id: Optional[str] = None, team_id: Optional[str] = None,
                 limit: int = 20, offset: Optional[str] = None) -> Dict[str, Any]:
        params = {"limit": limit}
        
        if workspace_id:
            params["workspace"] = workspace_id
        if team_id:
            params["team"] = team_id
        if offset:
            params["offset"] = offset
            
        return self._make_request("GET", "users", params=params)

    def get_user(self, user_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"users/{user_id}")

    def get_sections(self, project_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"projects/{project_id}/sections")

    def get_section(self, section_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"sections/{section_id}")

    def get_section_tasks(self, section_id: str, limit: int = 20, offset: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "limit": limit,
            "opt_fields": (
                "gid,name,completed,due_on,notes,"
                "assignee,assignee.gid,assignee.name,assignee.email,"
                "workspace,workspace.gid,workspace.name,"
                "projects,projects.gid,projects.name,"
                "parent,parent.gid,parent.name,"
                "created_at,modified_at"
            )
        }
        if offset:
            params["offset"] = offset
        
        return self._make_request("GET", f"sections/{section_id}/tasks", params=params)

    def get_time_periods(self, workspace_id: str, limit: int = 20, offset: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "workspace": workspace_id,
            "limit": limit,
            "opt_fields": "gid,name,start_on,end_on,period,workspace,parent"
        }
        if offset:
            params["offset"] = offset
        
        return self._make_request("GET", "time_periods", params=params)

    def get_goal_time_periods(self, workspace_id: str, limit: int = 20, offset: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "workspace": workspace_id,
            "limit": limit,
            "opt_fields": "gid,name,start_on,end_on,period,workspace,parent"
        }
        if offset:
            params["offset"] = offset
        
        return self._make_request("GET", "goals/time_periods", params=params)
