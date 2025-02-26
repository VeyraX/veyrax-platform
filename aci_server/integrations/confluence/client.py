from typing import Optional, Dict, Any, List
import requests
from fastapi import HTTPException

class ConfluenceClient:
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self._initialize_client()
        
    def _initialize_client(self):
        try:
            resources_url = "https://api.atlassian.com/oauth/token/accessible-resources"
            response = self.session.get(
                resources_url,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Accept': 'application/json'
                }
            )
            
            response.raise_for_status()
            resources = response.json()
            
            if not resources:
                raise HTTPException(status_code=404, detail="No Confluence resources available")
            
            self.cloud_id = resources[0]['id']
            self.base_url = f"https://api.atlassian.com/ex/confluence/{self.cloud_id}/rest/api"
            self.web_url = f"{resources[0]['url']}/wiki"
            
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
        except requests.exceptions.HTTPError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"API request failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_spaces(self, **kwargs) -> Dict[str, Any]:
        return self._make_request('GET', '/space', params=kwargs)

    def list_pages(self, **kwargs) -> Dict[str, Any]:
        return self._make_request('GET', '/content', params={
            **kwargs,
            'type': 'page',
            'expand': 'space,version,body.storage,ancestors'
        })

    def get_page(self, page_id: str) -> Dict[str, Any]:
        return self._make_request('GET', f'/content/{page_id}', params={
            'expand': 'space,version,body.storage,ancestors'
        })

    def create_page(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request('POST', '/content', data=data)

    def update_page(self, page_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request('PUT', f'/content/{page_id}', data=data)

    def search_content(self, **kwargs) -> Dict[str, Any]:
        return self._make_request('GET', '/content', params=kwargs)

    def _make_request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, params=params, json=data)
        response.raise_for_status()
        return response.json()