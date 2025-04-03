from typing import Optional, Dict, Any, List, Union
from .client import ConfluenceClient
from .schema import (
    SpaceSchema,
    PageSchema,
    PageCreateSchema,
    PageUpdateSchema,
    PageList,
    SpaceList,
    PageFilters,
    ApiResponse
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class ConfluenceService:
    def __init__(self, client: ConfluenceClient):
        self.client = client
        self.base_url = self.client.web_url
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[PageSchema, PageList, SpaceList], component_name: str = None) -> ApiResponse:
        tool_name = "confluence"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_spaces(self) -> ApiResponse:
        response = self.client.list_spaces(limit=100)

        spaces = []
        
        for space in response.get('results', []):
            if 'id' in space and not isinstance(space['id'], str):
                space['id'] = str(space['id'])
            spaces.append(SpaceSchema(**space))
            
        space_list = SpaceList(
            spaces=spaces,
            next_page=response.get('start', 0) + len(spaces) if len(spaces) == response.get('limit', 0) else None
        )
        
        return self.prepare_response(space_list, "ConfluenceSpaceList")

    def get_pages(self, filters: Optional[PageFilters] = None) -> ApiResponse:
        params = {'limit': filters.limit if filters else 50}
        if filters:
            if filters.space_id:
                params['spaceId'] = str(filters.space_id)
            if filters.title:
                params['title'] = filters.title

        response = self.client.list_pages(**params)
        pages = []
        
        for page in response.get('results', []):
            if '_links' in page and 'webui' in page.get('_links', {}):
                page['html_link'] = f"{self.base_url}{page['_links']['webui']}"
            pages.append(PageSchema(**page))
            
        page_list = PageList(
            pages=pages,
            next_page=response.get('start', 0) + len(pages) if len(pages) == response.get('limit', 0) else None
        )
        
        return self.prepare_response(page_list, "ConfluencePageCard")

    def get_page(self, page_id: str) -> ApiResponse:
        response = self.client.get_page(page_id)
        
        if '_links' in response and 'webui' in response.get('_links', {}):
            response['html_link'] = f"{self.base_url}{response['_links']['webui']}"
            
        page = PageSchema(**response)
        return self.prepare_response(page, "ConfluencePageCard")

    def create_page(self, page_data: PageCreateSchema) -> ApiResponse:
        data = {
            'type': 'page',
            'title': page_data.title,
            'space': {'key': page_data.spaceKey},
            'body': {
                'storage': {
                    'value': f"<p>{page_data.content}</p>",
                    'representation': 'storage'
                }
            }
        }
        if page_data.parentId:
            data['ancestors'] = [{'id': page_data.parentId}]
            
        response = self.client.create_page(data)
        
        if '_links' in response and 'webui' in response.get('_links', {}):
            response['html_link'] = f"{self.base_url}{response['_links']['webui']}"
            
        page = PageSchema(**response)
        return self.prepare_response(page, "ConfluencePageCard")

    def update_page(self, page_id: str, update_data: PageUpdateSchema) -> ApiResponse:
        current_page = self.client.get_page(page_id)
        
        data = {
            'version': {'number': update_data.version or current_page['version']['number'] + 1},
            'title': update_data.title or current_page['title'],
            'type': 'page',
            'body': {
                'storage': {
                    'value': update_data.content or current_page['body']['storage']['value'],
                    'representation': 'storage'
                }
            }
        }
        
        response = self.client.update_page(page_id, data)
        
        if '_links' in response and 'webui' in response.get('_links', {}):
            response['html_link'] = f"{self.base_url}{response['_links']['webui']}"
            
        page = PageSchema(**response)
        return self.prepare_response(page, "ConfluencePageCard")

    def search_content(self, cql: Optional[str] = None,
                      space_key: Optional[str] = None,
                      title: Optional[str] = None,
                      content_type: Optional[str] = 'page',
                      limit: int = 50) -> ApiResponse:
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
        pages = []
        
        for page in response.get('results', []):
            if 'id' in page and not isinstance(page['id'], str):
                page['id'] = str(page['id'])
            
            if 'space' not in page:
                page['space'] = {'key': space_key} if space_key else {}
            
            if 'version' not in page:
                page['version'] = {'number': 1}
            
            if '_links' in page and 'webui' in page.get('_links', {}):
                page['html_link'] = f"{self.base_url}{page['_links']['webui']}"
            
            pages.append(PageSchema(**page))
        
        page_list = PageList(
            pages=pages,
            next_page=response.get('start', 0) + len(pages) if len(pages) == response.get('limit', 0) else None
        )
        
        return self.prepare_response(page_list, "ConfluencePageCard")

    def delete_page(self, page_id: str) -> ApiResponse:
        self.client.delete_page(page_id)
        return ApiResponse(
            message=f"Page {page_id} deleted successfully"
        )