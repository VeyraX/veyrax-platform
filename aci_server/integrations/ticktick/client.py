import requests
from typing import Dict, Any, Optional
import json

class TickTickClient:
    BASE_URL = "https://api.ticktick.com"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_task(self, project_id: str, task_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/open/v1/project/{project_id}/task/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/open/v1/task",
            json=task_data,
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/open/v1/task/{task_id}",
            json=task_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def complete_task(self, project_id: str, task_id: str) -> None:
        response = requests.post(
            f"{self.BASE_URL}/open/v1/project/{project_id}/task/{task_id}/complete",
            headers=self.headers
        )
        response.raise_for_status()

    def delete_task(self, project_id: str, task_id: str) -> None:
        response = requests.delete(
            f"{self.BASE_URL}/open/v1/project/{project_id}/task/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()

    def get_projects(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/open/v1/project",
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()

    def get_project(self, project_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/open/v1/project/{project_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/open/v1/project",
            json=project_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/open/v1/project/{project_id}",
            json=project_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def delete_project(self, project_id: str) -> None:
        response = requests.delete(
            f"{self.BASE_URL}/open/v1/project/{project_id}",
            headers=self.headers
        )
        response.raise_for_status()

    def get_project_data(self, project_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/open/v1/project/{project_id}/data",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json() 