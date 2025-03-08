from typing import Optional, Dict, Any, List, Union
from .client import BrowserUseClient
from .schema import (
    RunTaskParams, TaskDetail, TaskStatus, TaskMedia, ApiResponse, Balance
)
import os
import json
from ..common.component_handler import load_components, prepare_components_auto

class BrowserUseService:
    def __init__(self, client: BrowserUseClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "browser_use"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def run_task(self, params: RunTaskParams) -> ApiResponse:
        """Start a new browser automation task."""
        task_data = params.dict(exclude_none=True)
        
        response = self.client.run_task(task_data)
        
        return self.prepare_response(response, "BrowserUseTaskCard")

    def stop_task(self, task_id: str) -> ApiResponse:
        """Stop a running browser automation task."""
        response = self.client.stop_task(task_id)
        
        return self.prepare_response(response, "BrowserUseTaskCard")

    def pause_task(self, task_id: str) -> ApiResponse:
        """Pause a running browser automation task."""
        response = self.client.pause_task(task_id)
        
        return self.prepare_response(response, "BrowserUseTaskCard")

    def resume_task(self, task_id: str) -> ApiResponse:
        """Resume a paused browser automation task."""
        response = self.client.resume_task(task_id)
        
        return self.prepare_response(response, "BrowserUseTaskCard")

    def get_task(self, task_id: str) -> ApiResponse:
        """Get detailed information about a task."""
        response = self.client.get_task(task_id)
        
        task_detail = TaskDetail(**response)
        
        return self.prepare_response(task_detail, "BrowserTaskDetailCard")

    def get_task_status(self, task_id: str) -> ApiResponse:
        """Get the current status of a task."""
        response = self.client.get_task_status(task_id)
        
        return self.prepare_response(response, "BrowserUseTaskStatusCard")

    def get_task_media(self, task_id: str) -> ApiResponse:
        """Get media links for a completed task."""
        response = self.client.get_task_media(task_id)
        
        task_media = TaskMedia(**response)
        
        return self.prepare_response(task_media, "BrowserUseTaskMediaCard")

    def list_tasks(self) -> ApiResponse:
        """List all tasks."""
        response = self.client.list_tasks()
        # Extract the tasks array from the response dictionary
        task_list = response.get('tasks', [])
        
        # Add missing required fields with default values if not present
        tasks = []
        for task in task_list:
            # Add empty steps list if missing
            if 'steps' not in task:
                task['steps'] = []
            tasks.append(TaskDetail(**task))
        
        return self.prepare_response(tasks, "BrowserTaskCard")

    def check_balance(self) -> ApiResponse:
        """Get the user's current API credit balance."""
        response = self.client.check_balance()
        
        balance = Balance(**response)
        
        return self.prepare_response(balance, "BrowserUseBalanceCard")

    def me(self) -> ApiResponse:
        """Check if the API key is valid."""
        response = self.client.me()
        
        return self.prepare_response(response, "BrowserUseAuthCard")

    def ping(self) -> ApiResponse:
        response = self.client.ping()
        
        return self.prepare_response(response, "BrowserUsePingCard")