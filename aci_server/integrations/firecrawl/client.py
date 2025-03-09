import requests
from typing import Dict, Any, Optional, List
from fastapi import HTTPException

class FirecrawlClient:
    BASE_URL = "https://api.firecrawl.dev/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
    
    def scrape(self, **params) -> Dict[str, Any]:
        return self._make_request('POST', '/scrape', json=params)
    
    def batch_scrape(self, **params) -> Dict[str, Any]:
        return self._make_request('POST', '/batch/scrape', json=params)
    
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        return self._make_request('GET', f'/batch/scrape/{batch_id}')
    
    def get_batch_errors(self, batch_id: str) -> Dict[str, Any]:
        return self._make_request('GET', f'/batch/scrape/{batch_id}/errors')
    
    def crawl(self, **params) -> Dict[str, Any]:
        return self._make_request('POST', '/crawl', json=params)
    
    def get_crawl_status(self, crawl_id: str) -> Dict[str, Any]:
        return self._make_request('GET', f'/crawl/{crawl_id}')
    
    def cancel_crawl(self, crawl_id: str) -> Dict[str, Any]:
        return self._make_request('DELETE', f'/crawl/{crawl_id}')
    
    def get_crawl_errors(self, crawl_id: str) -> Dict[str, Any]:
        return self._make_request('GET', f'/crawl/{crawl_id}/errors')
    
    def map_site(self, **params) -> Dict[str, Any]:
        return self._make_request('POST', '/map', json=params)
    
    def extract(self, **params) -> Dict[str, Any]:
        print(params)
        return self._make_request('POST', '/extract', json=params)
    
    def get_extract_status(self, extract_id: str) -> Dict[str, Any]:
        return self._make_request('GET', f'/extract/{extract_id}')
    
    def search(self, **params) -> Dict[str, Any]:
        return self._make_request('POST', '/search', json=params)
    
    def get_credit_usage(self) -> Dict[str, Any]:
        return self._make_request('GET', '/team/credit-usage')
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            try:
                error_detail = e.response.json().get('error', str(e))
            except:
                error_detail = str(e)
                
            raise HTTPException(status_code=status_code, detail=error_detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")
