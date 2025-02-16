from typing import Optional, Dict, Any
from fastapi import HTTPException
import requests
from .client import NotionClient
from .schema import (
    DatabaseList, Database, PageList, Page, 
    PageCreate, PageUpdate, PageFilters
)

class NotionService:
    def __init__(self, client: NotionClient):
        self.client = client

    def _handle_notion_response(self, response: Dict[str, Any]):
        """Handle potential error responses from Notion API"""
        if response.get('object') == 'error':
            status = response.get('status', 500)
            message = response.get('message', 'Unknown Notion API error')
            raise HTTPException(status_code=status, detail=message)
        return response

    def list_databases(self, start_cursor: Optional[str] = None) -> DatabaseList:
        params = {
            "filter": {
                "property": "object",
                "value": "database"
            },
            "page_size": 100
        }
        
        if start_cursor:
            params["start_cursor"] = start_cursor
        
        response = self.client.search_pages(**params)
        
        databases = []
        for db in response.get('results', []):
            title = " ".join(
                text.get("plain_text", "")
                for text in db.get('title', [])
            )
            databases.append({
                "id": db.get('id'),
                "title": title
            })
        
        return DatabaseList(
            items=databases,
            next_cursor=response.get('next_cursor')
        )

    def list_pages(self, database_id: str, 
                  start_cursor: Optional[str] = None,
                  filters: Optional[PageFilters] = None) -> PageList:
        
        params = {
            "page_size": 100
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
            
            pages.append({
                "id": page.get('id'),
                "title": title, 
                "created_time": page.get('created_time'),
                "last_edited_time": page.get('last_edited_time'),
                "archived": page.get('archived', False),
                "url": page.get('url')
            })
        
        return PageList(
            items=pages,
            next_cursor=response.get('next_cursor')
        )

    def get_page(self, page_id: str) -> Page:
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
            
            page_data = {
                "id": validated_response.get('id'),
                "title": title,
                "created_time": validated_response.get('created_time'),
                "last_edited_time": validated_response.get('last_edited_time'),
                "archived": validated_response.get('archived', False),
                "url": validated_response.get('url'),
                "content": validated_blocks.get('results', [])
            }
            
            return Page(**page_data)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

    def create_page(self, page_data: PageCreate) -> Page:
        payload = {
            "parent": {"database_id": page_data.parent_id},
            "properties": page_data.properties
        }
        if page_data.content:
            payload["children"] = page_data.content

        response = self.client.create_page(payload)
        return Page(**response)

    def update_page(self, page_id: str, page_data: PageUpdate) -> Page:
        payload = {}
        if page_data.properties:
            payload["properties"] = page_data.properties
        if page_data.archived is not None:
            payload["archived"] = page_data.archived

        response = self.client.update_page(page_id, payload)
        return Page(**response)

    def archive_page(self, page_id: str) -> Page:
        response = self.client.archive_page(page_id)
        return Page(**response)

    def search_pages(self, query: str, 
                    start_cursor: Optional[str] = None) -> PageList:
        response = self.client.search_pages(
            query=query,
            start_cursor=start_cursor
        )
        return PageList(
            items=response.get('results', []),
            next_cursor=response.get('next_cursor')
        )