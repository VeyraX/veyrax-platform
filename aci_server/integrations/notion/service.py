from typing import Optional, Dict, Any, List, Union
from fastapi import HTTPException
import requests
import os
from .client import NotionClient
from .schema import (
    DatabaseList, Database, PageList, Page, 
    PageCreate, PageUpdate, PageFilters, DatabaseProperties,
    SearchResult, ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class NotionService:
    def __init__(self, client: NotionClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[Page, PageList, Database, DatabaseList, SearchResult, DatabaseProperties], component_name: str = None) -> ApiResponse:
        tool_name = "notion"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def _handle_notion_response(self, response: Dict[str, Any]):
        """Handle potential error responses from Notion API"""
        if response.get('object') == 'error':
            status = response.get('status', 500)
            message = response.get('message', 'Unknown Notion API error')
            raise HTTPException(status_code=status, detail=message)
        return response

    def list_databases(self, start_cursor: Optional[str] = None, max_results: Optional[int] = None) -> ApiResponse:
        # Set up search parameters exactly as required by Notion API
        # The filter must be an object with 'value' and 'property' keys at the top level
        search_params = {
            # This is the correct way to filter specifically for databases
            "filter": {
                "value": "database",
                "property": "object"
            },
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time"
            },
            "page_size": min(max_results, 100) if max_results else 100
        }
        
        if start_cursor:
            search_params["start_cursor"] = start_cursor
        
        # Pass an empty query string
        response = self.client.search_pages(query="", **search_params)
        response = self._handle_notion_response(response)
        
        # For debugging
        print(f"Notion API response: {response}")
        
        databases = []
        for db in response.get('results', []):
            title = " ".join(
                text.get("plain_text", "")
                for text in db.get('title', [])
            )
            databases.append(Database(
                id=db.get('id'),
                title=title,
                url=db.get('url'),
                created_time=db.get('created_time'),
                last_edited_time=db.get('last_edited_time')
            ))
        
        database_list = DatabaseList(
            items=databases,
            next_cursor=response.get('next_cursor')
        )
        
        return self.prepare_response(database_list, "NotionDatabaseTable")

    def list_pages(self, database_id: str, 
                  start_cursor: Optional[str] = None,
                  filters: Optional[PageFilters] = None) -> ApiResponse:
        
        max_results = 100
        if filters and filters.max_results:
            max_results = min(filters.max_results, 100)
        
        params = {
            "page_size": max_results
        }
        
        if start_cursor:
            params["start_cursor"] = start_cursor
        if filters:
            if filters.filter_by:
                params["filter"] = filters.filter_by
            if filters.sort_by:
                params["sorts"] = filters.sort_by
        
        response = self.client.query_database(database_id, params)
        
        pages = []
        for page in response.get('results', []):
            title = ""
            properties = page.get('properties', {})
            title_prop = properties.get('Name') or properties.get('Title')
            if title_prop and title_prop.get('title'):
                title = " ".join(
                    text.get('plain_text', '')
                    for text in title_prop['title']
                )
            
            pages.append(Page(
                id=page.get('id'),
                title=title, 
                properties=properties,
                created_time=page.get('created_time'),
                last_edited_time=page.get('last_edited_time'),
                url=page.get('url'),
                parent=page.get('parent')
            ))
        
        page_list = PageList(
            items=pages,
            next_cursor=response.get('next_cursor')
        )
        
        return self.prepare_response(page_list, "NotionPageCard")

    def get_page(self, page_id: str) -> ApiResponse:
        try:
            response = self.client.get_page(page_id)
            validated_response = self._handle_notion_response(response)
            
            blocks_response = self.client.get_block_children(page_id)
            validated_blocks = self._handle_notion_response(blocks_response)
            
            title = ""
            properties = validated_response.get('properties', {})
            title_prop = properties.get('Name') or properties.get('Title')
            if title_prop and title_prop.get('title'):
                title = " ".join(
                    text.get('plain_text', '')
                    for text in title_prop['title']
                )
            
            page = Page(
                id=validated_response.get('id'),
                title=title,
                properties=properties,
                created_time=validated_response.get('created_time'),
                last_edited_time=validated_response.get('last_edited_time'),
                url=validated_response.get('url'),
                parent=validated_response.get('parent')
            )
            
            return self.prepare_response(page, "NotionPageCard")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

    def create_page(self, page_data: PageCreate) -> ApiResponse:
        try:
            payload = {
                "parent": page_data.parent.dict(),
                "properties": page_data.properties
            }
            if page_data.children:
                payload["children"] = page_data.children
            
            response = self.client.create_page(payload)
            
            if 'object' in response and response['object'] == 'error':
                raise HTTPException(
                    status_code=response.get('status', 500),
                    detail=response.get('message', 'Failed to create page in Notion')
                )
            
            title = self._extract_title(response.get("properties", {}))
            
            page = Page(
                id=response.get("id"),
                title=title,
                properties=response.get("properties", {}),
                created_time=response.get("created_time"),
                last_edited_time=response.get("last_edited_time"),
                url=response.get("url"),
                parent=response.get("parent")
            )
            
            return self.prepare_response(page, "NotionPageCard")
        except HTTPException:
            raise
        except Exception as e:
            print("Error type:", type(e))
            raise HTTPException(status_code=500, detail=str(e))

    def _extract_title(self, properties: dict) -> str:
        title_prop = properties.get("Name", properties.get("Title", {}))
        if "title" in title_prop and len(title_prop["title"]) > 0:
            title_parts = []
            for part in title_prop["title"]:
                if "plain_text" in part:
                    title_parts.append(part["plain_text"])
                elif "text" in part:
                    title_parts.append(part["text"].get("content", ""))
            return "".join(title_parts)
        return ""

    def update_page(self, page_id: str, page_data: PageUpdate) -> ApiResponse:
        try:
            payload = {
                "properties": page_data.properties
            }
            if hasattr(page_data, 'archived') and page_data.archived is not None:
                payload["archived"] = page_data.archived

            response = self.client.update_page(page_id, payload)
            
            if response.get('object') == 'error':
                raise HTTPException(
                    status_code=response.get('status', 500),
                    detail=response.get('message', 'Failed to update page in Notion')
                )

            title = self._extract_title(response.get("properties", {}))
            
            page = Page(
                id=response.get("id"),
                title=title,
                properties=response.get("properties", {}),
                created_time=response.get("created_time"),
                last_edited_time=response.get("last_edited_time"),
                url=response.get("url"),
                parent=response.get("parent")
            )
            
            return self.prepare_response(page, "NotionPageCard")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_database(self, database_id: str) -> ApiResponse:
        """Get database details including its schema"""
        response = self.client.get_database(database_id)
        validated_response = self._handle_notion_response(response)
        
        title = " ".join(
            text.get("plain_text", "")
            for text in validated_response.get('title', [])
        )
        
        database = Database(
            id=validated_response.get('id'),
            title=title,
            properties=validated_response.get('properties', {}),
            url=validated_response.get('url'),
            created_time=validated_response.get('created_time'),
            last_edited_time=validated_response.get('last_edited_time')
        )
        
        return self.prepare_response(database, "NotionDatabaseTable")

    def query_database(self, database_id: str, filter_data: Dict[str, Any] = None, 
                      sorts: List[Dict[str, Any]] = None, start_cursor: Optional[str] = None, 
                      page_size: int = 100) -> ApiResponse:
        params = {
            "page_size": min(page_size, 100)
        }
        
        if filter_data:
            params["filter"] = filter_data
            
        if sorts:
            params["sorts"] = sorts
            
        if start_cursor:
            params["start_cursor"] = start_cursor
        
        response = self.client.query_database(database_id, params)
        validated_response = self._handle_notion_response(response)
        
        pages = []
        for page in validated_response.get('results', []):
            title = ""
            properties = page.get('properties', {})
            title_prop = properties.get('Name') or properties.get('Title')
            if title_prop and title_prop.get('title'):
                title = " ".join(
                    text.get('plain_text', '')
                    for text in title_prop['title']
                )
            
            pages.append(Page(
                id=page.get('id'),
                title=title,
                properties=properties,
                created_time=page.get('created_time'),
                last_edited_time=page.get('last_edited_time'),
                url=page.get('url'),
                parent=page.get('parent')
            ))
        
        page_list = PageList(
            items=pages,
            next_cursor=validated_response.get('next_cursor')
        )
        
        return self.prepare_response(page_list, "NotionPageCard")

    def search(self, filters: Optional[PageFilters] = None, start_cursor: Optional[str] = None) -> ApiResponse:
        """Search for pages and databases in Notion"""
        params = {}
        
        if filters:
            if filters.query:
                params["query"] = filters.query
                
            if filters.sort_direction:
                direction = filters.sort_direction
                if direction.lower() in ["desc", "descending"]:
                    direction = "descending"
                elif direction.lower() in ["asc", "ascending"]:
                    direction = "ascending"
                else:
                    direction = "descending"
                    
                params["sort"] = {
                    "direction": direction,
                    "timestamp": "last_edited_time"
                }
                
            if filters.max_results:
                params["page_size"] = min(filters.max_results, 100)
        
        if start_cursor:
            params["start_cursor"] = start_cursor
            
        response = self.client.search_pages(**params)
        validated_response = self._handle_notion_response(response)
        
        results = []
        for item in validated_response.get('results', []):
            if item.get('object') == 'page':
                title = ""
                properties = item.get('properties', {})
                title_prop = properties.get('Name') or properties.get('Title')
                if title_prop and title_prop.get('title'):
                    title = " ".join(
                        text.get('plain_text', '')
                        for text in title_prop['title']
                    )
                
                results.append(Page(
                    id=item.get('id'),
                    title=title,
                    properties=properties,
                    created_time=item.get('created_time'),
                    last_edited_time=item.get('last_edited_time'),
                    url=item.get('url'),
                    parent=item.get('parent')
                ))
            elif item.get('object') == 'database':
                title = " ".join(
                    text.get("plain_text", "")
                    for text in item.get('title', [])
                )
                
                results.append(Database(
                    id=item.get('id'),
                    title=title,
                    properties=item.get('properties', {}),
                    url=item.get('url'),
                    created_time=item.get('created_time'),
                    last_edited_time=item.get('last_edited_time')
                ))
        
        search_result = SearchResult(
            items=results,
            next_cursor=validated_response.get('next_cursor')
        )
        
        return self.prepare_response(search_result, "NotionPageCard")

