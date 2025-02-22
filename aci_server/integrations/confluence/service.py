from typing import Optional, Dict, Any, List
from .client import ConfluenceClient
from .schema import (
    SpaceSchema,
    PageSchema,
    PageCreateSchema,
    PageUpdateSchema,
    PaginatedResponseSchema
)

class ConfluenceService:
    def __init__(self, client: ConfluenceClient):
        self.client = client
        self.base_url = self.client.web_url

    def get_spaces(self) -> PaginatedResponseSchema:
        """Get list of spaces"""
        response = self.client.list_spaces(limit=100)
        return PaginatedResponseSchema(
            results=response.get('results', []),
            start=response.get('start', 0),
            limit=response.get('limit', 100),
            size=len(response.get('results', []))
        )

    def get_pages(self, space_id: Optional[str] = None,
                 title: Optional[str] = None,
                 limit: int = 50) -> PaginatedResponseSchema:
        params = {'limit': limit}
        if space_id:
            params['spaceId'] = str(space_id)
        if title:
            params['title'] = title

        response = self.client.list_pages(**params)
        return PaginatedResponseSchema(**response)

    def get_page(self, page_id: str) -> PageSchema:
        response = self.client.get_page(page_id)
        return PageSchema(**response)

    def create_page(self, page_data: PageCreateSchema) -> PageSchema:
        data = {
            'type': 'page',
            'title': page_data.title,
            'space': {'id': page_data.spaceId},
            'body': {
                'storage': {
                    'value': page_data.content,
                    'representation': 'storage'
                }
            }
        }
        if page_data.parentId:
            data['ancestors'] = [{'id': page_data.parentId}]
            
        response = self.client.create_page(data)
        return PageSchema(**response)

    def update_page(self, page_id: str, update_data: PageUpdateSchema) -> PageSchema:
        current_page = self.get_page(page_id)
        
        data = {
            'version': {'number': update_data.version or current_page.version['number'] + 1},
            'title': update_data.title or current_page.title,
            'type': 'page',
            'body': {
                'storage': {
                    'value': update_data.content or current_page.body['storage']['value'],
                    'representation': 'storage'
                }
            }
        }
        
        response = self.client.update_page(page_id, data)
        return PageSchema(**response)

    def search_content(self, cql: Optional[str] = None,
                      space_key: Optional[str] = None,
                      title: Optional[str] = None,
                      content_type: Optional[str] = 'page',
                      limit: int = 50) -> PaginatedResponseSchema:
        params = {
            'limit': limit,
            'type': content_type
        }
        if cql:
            params['cql'] = cql
        if space_key:
            params['spaceKey'] = space_key
        if title:
            params['title'] = title

        response = self.client.search_content(**params)
        return PaginatedResponseSchema(**response)