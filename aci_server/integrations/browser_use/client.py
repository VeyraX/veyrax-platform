import requests
from typing import Dict, Any, Optional

class BrowserUseClient:
    BASE_URL = "https://api.browser-use.com/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def run_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/run-task",
            headers=self.headers,
            json=task_data
        )
        response.raise_for_status()
        return response.json()

    def stop_task(self, task_id: str) -> Any:
        response = requests.put(
            f"{self.BASE_URL}/stop-task?task_id={task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def pause_task(self, task_id: str) -> Any:
        response = requests.put(
            f"{self.BASE_URL}/pause-task?task_id={task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def resume_task(self, task_id: str) -> Any:
        response = requests.put(
            f"{self.BASE_URL}/resume-task?task_id={task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/task/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id: str) -> str:
        response = requests.get(
            f"{self.BASE_URL}/task/{task_id}/status",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_task_media(self, task_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/task/{task_id}/media",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_tasks(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/tasks",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def check_balance(self) -> Dict[str, int]:
        response = requests.get(
            f"{self.BASE_URL}/balance",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def me(self) -> bool:
        response = requests.get(
            f"{self.BASE_URL}/me",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def ping(self) -> Any:
        response = requests.get(
            f"{self.BASE_URL}/ping"
        )
        response.raise_for_status()
        return response.json()