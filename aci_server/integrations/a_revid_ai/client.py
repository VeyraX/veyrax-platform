from amazon_paapi import AmazonApi
import os




class RevidAIClient:
    def __init__(self, access_key: str):
        
        base_url = "https://www.revid.ai/api/public/v2/render"
        headers = {
            "key": api_key,
            "Content-Type": "application/json"
        }

        self.base_url = base_url
        self.headers = headers
        
    def _make_request(self, data):
        return requests.post(self.base_url, headers=self.headers, json=data)


    def create_video(self, creation_params):
        return self._make_request(creation_params)