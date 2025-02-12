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
        response = self.client.list_databases(start_cursor=start_cursor)
        return DatabaseList(
            items=response.get('results', []),
            next_cursor=response.get('next_cursor')
        )

    def list_pages(self, database_id: str, 
                  start_cursor: Optional[str] = None,
                  filters: Optional[PageFilters] = None) -> PageList:
        params = {"start_cursor": start_cursor}
        
        if filters:
            if filters.filter_by:
                params["filter"] = filters.filter_by
            if filters.sort_by:
                params["sorts"] = filters.sort_by

        response = self.client.list_pages(database_id, **params)
        return PageList(
            items=response.get('results', []),
            next_cursor=response.get('next_cursor')
        )

    def get_page(self, page_id: str) -> Page:
        try:
            response = self.client.get_page(page_id)
            validated_response = self._handle_notion_response(response)
            return Page(**validated_response)
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