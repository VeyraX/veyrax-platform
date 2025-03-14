import requests
from typing import Optional, Dict, Any, List

class FigmaClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
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

    def get_file(self, file_key: str) -> Dict[str, Any]:
        return self._make_request("GET", f"files/{file_key}")

    def get_file_nodes(self, file_key: str, node_ids: List[str]) -> Dict[str, Any]:
        params = {"ids": ",".join(node_ids)}
        return self._make_request("GET", f"files/{file_key}/nodes", params=params)

    def get_image(self, file_key: str, node_ids: List[str], format: str = "png", scale: float = 1) -> Dict[str, Any]:
        params = {
            "ids": ",".join(node_ids),
            "format": format,
            "scale": scale
        }
        return self._make_request("GET", f"images/{file_key}", params=params)

    def get_file_components(self, file_key: str) -> Dict[str, Any]:
        return self._make_request("GET", f"files/{file_key}/components")

    def get_component_sets(self, file_key: str) -> Dict[str, Any]:
        return self._make_request("GET", f"files/{file_key}/component_sets")

    def get_styles(self, file_key: str) -> Dict[str, Any]:
        return self._make_request("GET", f"files/{file_key}/styles")

    def get_me(self) -> Dict[str, Any]:
        return self._make_request("GET", "me")

    def get_team_projects(self, team_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"teams/{team_id}/projects")

    def get_team_components(self, team_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"teams/{team_id}/components")

    def get_team_component_sets(self, team_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"teams/{team_id}/component_sets")

    def get_team_styles(self, team_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"teams/{team_id}/styles")

    def get_project_files(self, project_id: str, branch_name: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if branch_name:
            params["branch_name"] = branch_name
        return self._make_request("GET", f"projects/{project_id}/files", params=params)
