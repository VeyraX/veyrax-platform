from google.cloud import tasks_v2
import json
import os
from typing import Dict, Any, List, Optional
import logging

class CloudTasksService:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.queue_name = os.environ.get("CLOUD_TASKS_QUEUE", "fild-processing")
        self.service_url = os.environ.get("CLOUD_RUN_SERVICE_URL")
        
        if not all([self.project_id, self.service_url]):
            raise ValueError("Missing required environment variables: GOOGLE_CLOUD_PROJECT, CLOUD_RUN_SERVICE_URL")
        
        credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if credentials_json:
            import json
            from google.oauth2 import service_account
            credentials_dict = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(credentials_dict)
            self.client = tasks_v2.CloudTasksClient(credentials=credentials)
        else:
            self.client = tasks_v2.CloudTasksClient()
            
        self.queue_path = self.client.queue_path(self.project_id, self.location, self.queue_name)

    def create_batch_processing_task(self, batch_data: Dict[str, Any], delay_seconds: int = 0) -> str:
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{self.service_url}/fild/cloud/process-batch",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps(batch_data).encode()
            }
        }
        
        if delay_seconds > 0:
            from google.protobuf import timestamp_pb2
            import time
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromSeconds(int(time.time() + delay_seconds))
            task["schedule_time"] = timestamp
        
        response = self.client.create_task(
            request={
                "parent": self.queue_path,
                "task": task
            }
        )
        
        logging.info(f"Created Cloud Task: {response.name}")
        return response.name

    def create_batches(self, cells_to_process: List[Dict], batch_size: int = 5) -> List[List[Dict]]:
        batches = []
        for i in range(0, len(cells_to_process), batch_size):
            batch = cells_to_process[i:i + batch_size]
            batches.append(batch)
        return batches 