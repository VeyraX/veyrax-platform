from typing import Optional, Dict, Any, List, Union, Tuple
from fastapi import HTTPException
import requests
import os
import re
from .client import NotionClient
from .schema import (
    DatabaseList, Database, PageList, Page, 
    PageCreate, PageUpdate, PageFilters, DatabaseProperties,
    SearchResult, ApiResponse, DatabaseCreate, UserList, NotionUser, DatabaseUpdate, UpdateDatabaseParams, UpdateDatabaseResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class NotionService:
    def __init__(self, client: NotionClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[Page, PageList, Database, DatabaseList, SearchResult, DatabaseProperties, UserList, NotionUser], component_name: str = None) -> ApiResponse:
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

    def format_page_id(self, page_id: str) -> str:
        """
        Check if the page ID is in the correct format with hyphens.
        If not, convert it from format like '1b25c159362a80c28aebc05f1f880bdc'
        to '1b25c159-362a-80c2-8aeb-c05f1f880bdc'.
        
        Args:
            page_id: The page ID to format
            
        Returns:
            Properly formatted page ID with hyphens
        """
        # Check if the ID already has hyphens
        if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', page_id):
            return page_id
            
        # Check if it's a 32-character hex string without hyphens
        if re.match(r'^[a-f0-9]{32}$', page_id):
            # Insert hyphens in the correct positions
            return f"{page_id[0:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:32]}"
            
        # If it doesn't match either pattern, return as is
        return page_id

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
                params["sorts"] = [filters.sort_by]  # Wrap sort_by in an array
        
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
        # Format the page ID to ensure it has the correct format
        formatted_page_id = self.format_page_id(page_id)
        
        response = self.client.get_page(formatted_page_id)
        validated_response = self._handle_notion_response(response)
        
        blocks_response = self.client.get_block_children(formatted_page_id)
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
        
    def _find_database_blocks(self, children: Optional[List[Dict[str, Any]]] = None):
        if children is None:
            return [], None, []

        new_children = []
        database_block = None
        rest_children = []
        for child in children:
            if child.get('type') == 'database':
                database_block = child
                continue
            if database_block:
                rest_children.append(child)
            else:
                new_children.append(child)
        return new_children, database_block, rest_children

    def create_page(self, page_data: PageCreate) -> ApiResponse:
        # Process properties to handle people properties correctly
        processed_properties = {}
        for prop_name, prop_value in page_data.properties.items():
            if isinstance(prop_value, dict) and 'people' in prop_value:
                # Handle people property
                people_list = prop_value.get('people', [])
                processed_people = []
                
                for person in people_list:
                    if isinstance(person, dict) and 'id' in person:
                        # If it's already a properly formatted person object, use it
                        processed_people.append({"id": person['id']})
                    elif isinstance(person, dict) and 'object' in person and person.get('object') == 'user':
                        # If it's a user object with an ID, extract the ID
                        user_id = person.get('id')
                        if user_id:
                            processed_people.append({"id": user_id})
                
                processed_properties[prop_name] = {
                    'people': processed_people
                }
            else:
                processed_properties[prop_name] = prop_value
        
        # Create the page
        payload = {
            "parent": page_data.parent.dict(),
            "properties": processed_properties
        }

        new_children, database_block, rest_children = self._find_database_blocks(page_data.children)
        
        payload["children"] = new_children
        
        response = self.client.create_page(payload)

        page_id = response.get('id')

        if database_block:
            database = database_block.get("database", {})

            # Convert properties to ensure compatibility with Notion API
            properties = database.get("properties", {})
            modified_properties = {}
            
            # Convert status properties to select properties (Notion API limitation)
            for prop_name, prop_value in properties.items():
                if "status" in prop_value:
                    # Convert status to select
                    modified_properties[prop_name] = {
                        "select": {
                            "options": prop_value.get("status", {}).get("options", [])
                        }
                    }
                else:
                    modified_properties[prop_name] = prop_value
            
            transformed_obj = {
                "parent": {
                    "type": "page_id",
                    "page_id": page_id
                },
                "is_inline": True,
                "title": database.get("title", []),
                "properties": modified_properties
            }
        
            db = self.client.create_database(transformed_obj)

        if len(rest_children) > 0:
            self.client.append_block_children(page_id, rest_children)
        
        if 'object' in response and response['object'] == 'error':
            raise HTTPException(
                status_code=response.get('status', 500),
                detail=response.get('message', 'Failed to create page in Notion')
            )
            
        # Extract the title from properties
        title = self._extract_title(response.get('properties', {}))
        
        # Get the properties
        properties = response.get('properties', {})
        
        # Create a Page object
        page = Page(
            id=response.get('id'),
            title=title,
            properties=properties,
            created_time=response.get('created_time'),
            last_edited_time=response.get('last_edited_time'),
            url=response.get('url'),
            parent=response.get('parent')
        )
        
        # Wrap the page in a PageList to make it compatible with the NotionPageCard component
        page_list = PageList(items=[page], next_cursor=None)
        
        return self.prepare_response(page_list, "NotionPageCard")

    def create_database(self, database_data: DatabaseCreate) -> ApiResponse:
        # Process properties to replace status properties with select properties
        # and convert PropertyType objects to dictionaries
        processed_properties = {}
        has_title_property = False
        
        for prop_name, prop_value in database_data.properties.items():
            # Convert PropertyType objects to dictionaries if needed
            if hasattr(prop_value, "dict") or hasattr(prop_value, "model_dump"):
                # Convert Pydantic model to dict
                if hasattr(prop_value, "model_dump"):
                    # Pydantic v2
                    prop_dict = prop_value.model_dump(exclude_none=True)
                else:
                    # Pydantic v1
                    prop_dict = prop_value.dict(exclude_none=True)
                
                # Check if this is a title property
                if prop_dict.get('type') == 'title':
                    has_title_property = True
                
                # If it's a status property, replace it with a select property
                if prop_dict.get('type') == 'status' and 'status' in prop_dict:
                    # Convert status to select
                    select_options = []
                    if 'options' in prop_dict.get('status', {}):
                        select_options = prop_dict['status']['options']
                    
                    processed_properties[prop_name] = {
                        'select': {
                            'options': select_options
                        }
                    }
                else:
                    # Extract the specific property configuration based on type
                    # e.g., if type is 'select', include only the 'select' object
                    prop_type = prop_dict.get('type')
                    if prop_type and prop_type in prop_dict:
                        processed_properties[prop_name] = {
                            'type': prop_type,
                            prop_type: prop_dict[prop_type]
                        }
                    elif prop_type:
                        # Fallback to simple type: {} format for empty configs
                        processed_properties[prop_name] = {
                            'type': prop_type,
                            prop_type: {}
                        }
            elif isinstance(prop_value, dict):
                # It's already a dict
                # Check if this is a title property
                if prop_value.get('type') == 'title':
                    has_title_property = True
                
                # Check if it has status and replace
                if 'status' in prop_value:
                    # Convert status to select
                    select_options = []
                    if 'options' in prop_value.get('status', {}):
                        select_options = prop_value['status']['options']
                    
                    processed_properties[prop_name] = {
                        'select': {
                            'options': select_options
                        }
                    }
                else:
                    processed_properties[prop_name] = prop_value
            else:
                # Not a dict or PropertyType, just use as is (shouldn't happen)
                processed_properties[prop_name] = prop_value
        
        # If no title property, add one
        if not has_title_property:
            processed_properties["Name"] = {
                "id": "title",
                "name": "Name",
                "type": "title",
                "title": {}
            }
        
        # Ensure the title field is correctly formatted with a default if missing
        title = database_data.title
        if title is None or title == [] or len(title) == 0:
            # Set a default title if title is missing
            title = [{"type": "text", "text": {"content": "Untitled"}}]
        elif not isinstance(title, list):
            # Convert title to proper format if it's not already a list
            title = [{"type": "text", "text": {"content": str(title)}}]
        else:
            # Validate and fix title items if they exist but are malformed
            fixed_title = []
            for item in title:
                if isinstance(item, dict):
                    if "text" in item and "type" in item and isinstance(item["text"], dict) and "content" in item["text"]:
                        # Correct order of keys if needed
                        fixed_item = {
                            "type": item["type"],
                            "text": item["text"]
                        }
                        fixed_title.append(fixed_item)
                    elif "content" in item:
                        # Simple content string
                        fixed_title.append({"type": "text", "text": {"content": item["content"]}})
                    else:
                        # Default to empty string if structure is unclear
                        fixed_title.append({"type": "text", "text": {"content": ""}})
                else:
                    # Not a dict, convert to string
                    fixed_title.append({"type": "text", "text": {"content": str(item)}})
            
            if not fixed_title:
                # If after fixing there are no valid items, use default
                title = [{"type": "text", "text": {"content": "Untitled"}}]
            else:
                title = fixed_title
        
        payload = {
            "parent": database_data.parent.dict() if hasattr(database_data.parent, "dict") else database_data.parent,
            "title": title,
            "properties": processed_properties,
            "is_inline": database_data.is_inline
        }
        
        response = self.client.create_database(payload)
        
        if 'object' in response and response['object'] == 'error':
            raise HTTPException(
                status_code=response.get('status', 500),
                detail=response.get('message', 'Failed to create database in Notion')
            )
        
        # Extract the title
        title = " ".join(
            text.get("plain_text", "")
            for text in response.get('title', [])
        )
        
        # Create a Database object
        database = Database(
            id=response.get('id'),
            title=title,
            properties=response.get('properties'),
            url=response.get('url'),
            created_time=response.get('created_time'),
            last_edited_time=response.get('last_edited_time')
        )
        
        return self.prepare_response(database, "NotionDatabaseCard")

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
        # Format the page ID to ensure it has the correct format
        formatted_page_id = self.format_page_id(page_id)
        
        payload = {
            "properties": page_data.properties
        }
        
        response = self.client.update_page(formatted_page_id, payload)
        
        if 'object' in response and response['object'] == 'error':
            raise HTTPException(
                status_code=response.get('status', 500),
                detail=response.get('message', 'Failed to update page in Notion')
            )
            
        # Extract the title from properties
        title = self._extract_title(response.get('properties', {}))
        
        # Create a Page object
        page = Page(
            id=response.get('id'),
            title=title,
            properties=response.get('properties', {}),
            created_time=response.get('created_time'),
            last_edited_time=response.get('last_edited_time'),
            url=response.get('url'),
            parent=response.get('parent')
        )
        
        return self.prepare_response(page, "NotionPageCard")

    def format_people_property(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        people = []
        for user_id in user_ids:
            # Format the user ID to ensure it has the correct format
            formatted_user_id = self.format_page_id(user_id)
            
            # For each user ID, we need to determine if it's a person or bot
            try:
                user_response = self.client.get_user(formatted_user_id)
                
                if 'object' in user_response and user_response['object'] == 'error':
                    continue  # Skip this user if there's an error
                
                user_type = user_response.get('type')
                
                if user_type == 'person':
                    people.append({
                        "id": formatted_user_id
                    })
                elif user_type == 'bot':
                    people.append({
                        "id": formatted_user_id
                    })
            except Exception:
                # If we can't get the user, skip it
                continue
                
        return people

    def _block_to_dict(self, block) -> Dict[str, Any]:
        """
        Convert a Block object to a dictionary suitable for the Notion API.
        
        Args:
            block: A Block object
            
        Returns:
            A dictionary representation of the block
        """
        # Convert to dict using model_dump if available (Pydantic v2) or dict() (Pydantic v1)
        if hasattr(block, "model_dump"):
            block_dict = block.model_dump(exclude_none=True)
        else:
            block_dict = block.dict(exclude_none=True)
            
        # Add any missing required fields for Notion API
        if "object" not in block_dict:
            block_dict["object"] = "block"
         
        # Special handling for table blocks
        if block_dict.get("type") == "table" and "children" in block_dict:
            # For table blocks, children need to be inside the table property
            table_rows = block_dict.pop("children", [])
            
            # Convert any row children to dictionaries
            serialized_rows = []
            for row in table_rows:
                if hasattr(row, "dict") or hasattr(row, "model_dump"):
                    serialized_rows.append(self._block_to_dict(row))
                else:
                    row_dict = row.copy()
                    if "object" not in row_dict:
                        row_dict["object"] = "block"
                    serialized_rows.append(row_dict)
            
            # Add children to the table property
            block_dict["table"]["children"] = serialized_rows
            
        return block_dict

    def _serialize_block(self, block: Any) -> Dict[str, Any]:
        """
        Serialize a block object or dictionary to the format required by Notion API.
        
        Args:
            block: A Block object or dictionary
            
        Returns:
            A dictionary representation of the block ready for the Notion API
        """
        # Convert block object to dictionary
        if hasattr(block, "dict") or hasattr(block, "model_dump"):
            # It's a Block object
            return self._block_to_dict(block)
        elif isinstance(block, dict):
            # It's already a dict, dispatch to specific handler based on type
            block_type = block.get("type")
            if block_type == "table":
                return self._serialize_table_block(block)
            elif block_type == "column_list":
                return self._serialize_column_list_block(block)
            else:
                # Default handling for other block types
                block_dict = block.copy()
                if "object" not in block_dict:
                    block_dict["object"] = "block"
                return block_dict
        else:
            # Not a dict or Block object, convert to paragraph
            return {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": str(block)}}]
                }
            }

    def _serialize_table_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize a table block, properly handling its children rows.
        
        Args:
            block: A dictionary representing a table block
            
        Returns:
            A properly formatted table block dictionary
        """
        # Create a new dict to avoid modifying the original
        block_dict = {
            "object": "block",
            "type": "table",
            "table": {}
        }
        
        # Copy all table properties (except children)
        if "table" in block and isinstance(block["table"], dict):
            for key, value in block["table"].items():
                if key != "children":  # Don't copy children yet
                    block_dict["table"][key] = value
        
        # Ensure necessary table properties exist
        if "table_width" not in block_dict["table"] and "table_width" in block:
            block_dict["table"]["table_width"] = block["table_width"]
            
        if "has_column_header" not in block_dict["table"] and "has_column_header" in block:
            block_dict["table"]["has_column_header"] = block["has_column_header"]
            
        if "has_row_header" not in block_dict["table"] and "has_row_header" in block:
            block_dict["table"]["has_row_header"] = block["has_row_header"]
        
        # Process children wherever they might be
        table_rows = []
        
        # First check for children in the table property
        if "table" in block and isinstance(block["table"], dict) and "children" in block["table"]:
            table_rows.extend(block["table"]["children"])
        
        # Then check for children at the top level
        if "children" in block:
            table_rows.extend(block["children"])
        
        # Serialize each table row
        serialized_rows = []
        for row in table_rows:
            if isinstance(row, dict) and "object" not in row:
                row = row.copy()
                row["object"] = "block"
            serialized_rows.append(self._serialize_block(row))
        
        # Set the children inside the table property
        block_dict["table"]["children"] = serialized_rows
        
        return block_dict

    def _serialize_column_list_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize a column_list block, handling its column children.
        
        Args:
            block: A dictionary representing a column_list block
            
        Returns:
            A properly formatted column_list block dictionary
        """
        # Create a new dict to avoid modifying the original
        block_dict = {
            "object": "block",
            "type": "column_list",
            "column_list": {}
        }
        
        # Copy any column_list properties
        if "column_list" in block and isinstance(block["column_list"], dict):
            for key, value in block["column_list"].items():
                block_dict["column_list"][key] = value
        
        # Handle columns if present
        columns = []
        if "children" in block:
            columns.extend(block["children"])
        
        # Serialize each column
        if columns:
            serialized_columns = []
            for column in columns:
                # Process the column block
                column_dict = self._serialize_block(column)
                
                # If this column has children, process them too
                if "children" in column:
                    column_children = column.get("children", [])
                    serialized_column_children = []
                    
                    for child in column_children:
                        serialized_column_children.append(self._serialize_block(child))
                    
                    # Replace the children with serialized ones
                    column_dict["children"] = serialized_column_children
                
                serialized_columns.append(column_dict)
            
            # Add serialized columns back to the block
            block_dict["children"] = serialized_columns
        
        return block_dict

    def append_block_children(self, block_id: str, children: List[Any]) -> ApiResponse:
        """
        Append blocks to a page or block.
        
        Args:
            block_id: The ID of the block to append to (can be a page ID)
            children: The blocks to append (can be Block objects or dictionaries)
            
        Returns:
            The response from the Notion API
        """
        # Format the block ID to ensure it has the correct format
        formatted_block_id = self.format_page_id(block_id)
        
        # Enable for troubleshooting
        debug_mode = False
        if debug_mode:
            import json
            print(f"Original input: {json.dumps(children, indent=2)}")
        
        # Process the blocks to match Notion API structure
        api_formatted_children = []
        for child in children:
            if isinstance(child, dict) and child.get("type") == "table":
                # Special handling for table blocks to match Notion API format
                table_block = {
                    "object": "block",
                    "type": "table",
                    "table": {
                        # Copy table properties
                        "table_width": child.get("table", {}).get("table_width", 3),
                    }
                }
                
                # Copy other table properties
                for key in ["has_column_header", "has_row_header"]:
                    if key in child.get("table", {}):
                        table_block["table"][key] = child["table"][key]
                
                # Get the table rows if they exist
                if "children" in child and isinstance(child["children"], list):
                    # Format the rows
                    formatted_rows = []
                    for row in child["children"]:
                        if isinstance(row, dict):
                            # Ensure each row has required fields
                            row_copy = row.copy()
                            row_copy["object"] = "block"
                            formatted_rows.append(row_copy)
                    
                    # Add the formatted rows to the table.children array
                    table_block["table"]["children"] = formatted_rows
                else:
                    # Create a default empty row if no rows provided
                    table_block["table"]["children"] = [{
                        "object": "block",
                        "type": "table_row",
                        "table_row": {
                            "cells": [[] for _ in range(table_block["table"]["table_width"])]
                        }
                    }]
                
                # Add the formatted table block
                api_formatted_children.append(table_block)
            else:
                # For non-table blocks, just ensure object field
                if isinstance(child, dict):
                    child_copy = child.copy()
                    if "object" not in child_copy:
                        child_copy["object"] = "block"
                    api_formatted_children.append(child_copy)
                else:
                    # Use the normal serializer for other blocks
                    serialized_child = self._serialize_block(child)
                    api_formatted_children.append(serialized_child)
        
        if debug_mode:
            import json
            print(f"API formatted: {json.dumps(api_formatted_children, indent=2)}")
        
        # Call the client with the properly formatted children
        response = self.client.append_block_children(formatted_block_id, api_formatted_children)
        
        if 'object' in response and response['object'] == 'error':
            raise HTTPException(
                status_code=response.get('status', 500),
                detail=response.get('message', 'Failed to append blocks in Notion')
            )
        
        # Create a custom response that matches the ApiResponse model
        page = Page(
            id=formatted_block_id,
            title="Block updated",
            properties={},
            url=f"https://www.notion.so/{formatted_block_id.replace('-', '')}"
        )
        
        return self.prepare_response(page, "NotionPageCard")

    def append_media(self, block_id: str, media_type: str, url: str, caption: Optional[str] = None, name: Optional[str] = None) -> ApiResponse:
        """
        Append a media block (file, image, or PDF) to a page or block.
        
        Args:
            block_id: The ID of the block to append to (can be a page ID)
            media_type: Type of media block: 'file', 'image', or 'pdf'
            url: URL of the media file
            caption: Optional caption for the media
            name: Optional filename for file blocks
            
        Returns:
            The response from the Notion API
        """
        # Validate media_type
        if media_type not in ['file', 'image', 'pdf']:
            raise ValueError(f"Invalid media_type: {media_type}. Must be one of: 'file', 'image', or 'pdf'")
        
        # Format the block ID to ensure it has the correct format
        formatted_block_id = self.format_page_id(block_id)
        
        # Create the caption list if provided
        caption_list = None
        if caption:
            caption_list = [
                {
                    "type": "text",
                    "text": {
                        "content": caption
                    }
                }
            ]
        
        # Create the media block based on the media_type
        media_block = {
            "object": "block",
            "type": media_type,
            media_type: {
                "type": "external",
                "external": {
                    "url": url
                }
            }
        }
        
        # Add caption if provided
        if caption_list:
            media_block[media_type]["caption"] = caption_list
        
        # Add name if provided for file blocks
        if name and media_type == "file":
            media_block[media_type]["name"] = name
        
        # Call the client with the properly formatted block
        response = self.client.append_block_children(formatted_block_id, [media_block])
        
        if 'object' in response and response['object'] == 'error':
            raise HTTPException(
                status_code=response.get('status', 500),
                detail=response.get('message', f'Failed to append {media_type} block in Notion')
            )
        
        # Create a custom response that matches the ApiResponse model
        page = Page(
            id=formatted_block_id,
            title=f"Added {media_type} block",
            properties={},
            url=f"https://www.notion.so/{formatted_block_id.replace('-', '')}"
        )
        
        return self.prepare_response(page, "NotionPageCard")

    def create_page_with_database(self, page_data: PageCreate, database_id: str) -> ApiResponse:
        # Format the database ID to ensure it has the correct format
        formatted_database_id = self.format_page_id(database_id)
        
        # Create the page first
        page_response = self.create_page(page_data)
        
        # Get the page ID from the response
        page_id = page_response.data.items[0].id
        
        # Create the database reference block
        database_block = {
            "object": "block",
            "type": "link_to_page",
            "link_to_page": {
                "type": "database_id",
                "database_id": formatted_database_id
            }
        }
        
        # Append the database reference to the page
        self.client.append_block_children(page_id, [database_block])
        
        # Return the original page response
        return page_response

    def get_database(self, database_id: str) -> ApiResponse:
        """Get database details including its schema"""
        # Format the database ID to ensure it has the correct format
        formatted_database_id = self.format_page_id(database_id)
        
        response = self.client.get_database(formatted_database_id)
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

    def update_database(self, database_id: str, database_update: DatabaseUpdate) -> ApiResponse:
        """Update database title, description, or properties"""
        # Format the database ID to ensure it has the correct format
        formatted_database_id = self.format_page_id(database_id)
        
        # Prepare the payload with only non-None values
        payload = {}
        if database_update.title is not None:
            payload["title"] = database_update.title
            
        if database_update.description is not None:
            payload["description"] = database_update.description
            
        if database_update.properties is not None:
            # Process properties to convert PropertyType objects to dictionaries if needed
            processed_properties = {}
            for prop_name, prop_value in database_update.properties.items():
                # Convert PropertyType objects to dictionaries if needed
                if hasattr(prop_value, "dict") or hasattr(prop_value, "model_dump"):
                    # Convert Pydantic model to dict
                    if hasattr(prop_value, "model_dump"):
                        # Pydantic v2
                        prop_dict = prop_value.model_dump(exclude_none=True)
                    else:
                        # Pydantic v1
                        prop_dict = prop_value.dict(exclude_none=True)
                    
                    # If it's a status property, Notion API doesn't support updating it
                    if prop_dict.get('type') == 'status':
                        continue  # Skip status properties as they can't be updated via API
                        
                    # If it's a formula property, Notion API doesn't support updating it
                    if prop_dict.get('type') == 'formula':
                        continue  # Skip formula properties as they can't be updated via API
                    
                    # If it's a select property, Notion API doesn't support updating it
                    if prop_dict.get('type') == 'select':
                        # You can only add new properties, not update existing ones
                        if 'id' in prop_dict:
                            continue  # Skip existing select properties
                    
                    # Extract the specific property configuration based on type
                    prop_type = prop_dict.get('type')
                    if prop_type and prop_type in prop_dict:
                        # For new properties in update operations, don't include id/name in the payload
                        # as they're in the property key already
                        update_prop = {
                            'type': prop_type,
                            prop_type: prop_dict[prop_type]
                        }
                        processed_properties[prop_name] = update_prop
                    elif prop_type:
                        # Fallback to simple type: {} format for empty configs
                        processed_properties[prop_name] = {
                            'type': prop_type,
                            prop_type: {}
                        }
                else:
                    # It's already a dict, keep as is
                    processed_properties[prop_name] = prop_value
            
            payload["properties"] = processed_properties
        
        # Make the API call only if we have something to update
        if payload:
            response = self.client.update_database(formatted_database_id, payload)
            validated_response = self._handle_notion_response(response)
            
            # Extract the title
            title = " ".join(
                text.get("plain_text", "")
                for text in validated_response.get('title', [])
            )
            
            # Create a Database object
            database = Database(
                id=validated_response.get('id'),
                title=title,
                properties=validated_response.get('properties', {}),
                url=validated_response.get('url'),
                created_time=validated_response.get('created_time'),
                last_edited_time=validated_response.get('last_edited_time')
            )
            
            return self.prepare_response(database, "NotionDatabaseTable")
        else:
            # If no updates provided, just get the current database
            return self.get_database(formatted_database_id)

    def query_database(self, database_id: str, filter_data: Dict[str, Any] = None, 
                      sorts: List[Dict[str, Any]] = None, start_cursor: Optional[str] = None, 
                      page_size: int = 100) -> ApiResponse:
        # Format the database ID to ensure it has the correct format
        formatted_database_id = self.format_page_id(database_id)
        
        params = {
            "page_size": min(page_size, 100)
        }
        
        if filter_data:
            # Convert filter_data to dict if it's a Pydantic model
            if hasattr(filter_data, "model_dump"):
                # Pydantic v2
                filter_dict = filter_data.model_dump(exclude_none=True)
            elif hasattr(filter_data, "dict"):
                # Pydantic v1
                filter_dict = filter_data.dict(exclude_none=True)
            else:
                filter_dict = filter_data
                
            # Handle compound filters
            if "and_" in filter_dict:
                filter_dict["and"] = filter_dict.pop("and_")
            if "or_" in filter_dict:
                filter_dict["or"] = filter_dict.pop("or_")
                
            params["filter"] = filter_dict
            
        if sorts:
            # Convert each sort object to dict if it's a Pydantic model
            serialized_sorts = []
            for sort in sorts:
                if hasattr(sort, "model_dump"):
                    # Pydantic v2
                    sort_dict = sort.model_dump(exclude_none=True)
                elif hasattr(sort, "dict"):
                    # Pydantic v1
                    sort_dict = sort.dict(exclude_none=True)
                else:
                    sort_dict = sort
                serialized_sorts.append(sort_dict)
            params["sorts"] = serialized_sorts
            
        if start_cursor:
            params["start_cursor"] = start_cursor
        
        response = self.client.query_database(formatted_database_id, params)
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
        # Set up search parameters
        search_params = {}
        
        if filters:
            if filters.query:
                search_params["query"] = filters.query
            if filters.sort_direction:
                search_params["sort"] = {
                    "direction": filters.sort_direction,
                    "timestamp": "last_edited_time"
                }
            if filters.max_results:
                search_params["page_size"] = min(filters.max_results, 100)
        
        if start_cursor:
            search_params["start_cursor"] = start_cursor
        
        # Execute the search
        response = self.client.search_pages(**search_params)
        
        # Process the results
        items = []
        for item in response.get('results', []):
            if item.get('object') == 'page':
                # Extract title from properties
                title = ""
                properties = item.get('properties', {})
                title_prop = properties.get('Name') or properties.get('Title')
                if title_prop and title_prop.get('title'):
                    title = " ".join(
                        text.get('plain_text', '')
                        for text in title_prop['title']
                    )
                
                items.append(Page(
                    id=item.get('id'),
                    title=title,
                    properties=properties,
                    created_time=item.get('created_time'),
                    last_edited_time=item.get('last_edited_time'),
                    url=item.get('url'),
                    parent=item.get('parent')
                ))
            elif item.get('object') == 'database':
                # Extract title from title array
                title = " ".join(
                    text.get('plain_text', '')
                    for text in item.get('title', [])
                )
                
                items.append(Database(
                    id=item.get('id'),
                    title=title,
                    properties=item.get('properties'),
                    url=item.get('url'),
                    created_time=item.get('created_time'),
                    last_edited_time=item.get('last_edited_time')
                ))
        
        search_result = SearchResult(
            items=items,
            next_cursor=response.get('next_cursor')
        )
        
        return self.prepare_response(search_result, "NotionPageCard")

    def get_users(self, start_cursor: Optional[str] = None, page_size: Optional[int] = None) -> ApiResponse:
        params = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = min(page_size, 100)
            
        # Pass the params to the client method
        response = self.client.get_users(**params)
        
        users = []
        for user in response.get('results', []):
            users.append(NotionUser(
                id=user.get('id'),
                name=user.get('name'),
                avatar_url=user.get('avatar_url'),
                type=user.get('type'),
                person=user.get('person'),
                bot=user.get('bot')
            ))
        
        user_list = UserList(
            items=users,
            next_cursor=response.get('next_cursor')
        )
        
        return self.prepare_response(user_list, "NotionUserList")
            
    def get_user(self, user_id: str) -> ApiResponse:
        formatted_user_id = self.format_page_id(user_id)
        
        response = self.client.get_user(formatted_user_id)
        
        if 'object' in response and response['object'] == 'error':
            raise HTTPException(
                status_code=response.get('status', 500),
                detail=response.get('message', 'Failed to get user from Notion')
            )
        
        user = NotionUser(
            id=response.get('id'),
            name=response.get('name'),
            avatar_url=response.get('avatar_url'),
            type=response.get('type'),
            person=response.get('person'),
            bot=response.get('bot')
        )
        
        return self.prepare_response(user, "NotionUser")

