from typing import Optional, Dict, Any, List, Union, Tuple
from fastapi import HTTPException
import requests
import os
from .client import NotionClient
from .schema import (
    DatabaseList, Database, PageList, Page, 
    PageCreate, PageUpdate, PageFilters, DatabaseProperties,
    SearchResult, ApiResponse, DatabaseCreate, UserList, NotionUser
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
        try:            
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
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

    def create_database(self, database_data: DatabaseCreate) -> ApiResponse:
        try:
            # Process properties to replace status properties with select properties
            processed_properties = {}
            for prop_name, prop_value in database_data.properties.items():
                # If it's a status property, replace it with a select property
                if isinstance(prop_value, dict) and 'status' in prop_value:
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
            
            payload = {
                "parent": database_data.parent.dict(),
                "title": database_data.title,
                "properties": processed_properties,
                "is_inline": database_data.is_inline
            }
            
            response = self.client.create_database(payload)
            
            print(f"Notion API response for database creation: {response}")
            
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
        except requests.exceptions.RequestException as e:
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
            
            response = self.client.update_page(page_id, payload)
            
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
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

    def append_block_children(self, block_id: str, children: List[Dict[str, Any]]) -> ApiResponse:
        """
        Append blocks to a page or block.
        
        Args:
            block_id: The ID of the block to append to (can be a page ID)
            children: The blocks to append
            
        Returns:
            The response from the Notion API
        """
        try:
            response = self.client.append_block_children(block_id, children)
            
            print(f"Notion API response for append block children: {response}")
            
            if 'object' in response and response['object'] == 'error':
                raise HTTPException(
                    status_code=response.get('status', 500),
                    detail=response.get('message', 'Failed to append blocks in Notion')
                )
            
            # Create a custom response that matches the ApiResponse model
            # We'll use a Page object with the block_id as the page ID
            page = Page(
                id=block_id,
                title="Block updated",
                properties={},
                url=f"https://www.notion.so/{block_id.replace('-', '')}"
            )
            
            return self.prepare_response(page, "NotionPageCard")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

    def create_page_with_database(self, page_data: PageCreate, database_id: str) -> ApiResponse:
        """
        Create a page and append a database reference to it.
        
        Args:
            page_data: The page data to create
            database_id: The ID of the database to reference
            
        Returns:
            The created page with the database reference
        """
        try:
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
                    "database_id": database_id
                }
            }
            
            # Append the database reference to the page
            self.client.append_block_children(page_id, [database_block])
            
            # Return the original page response
            return page_response
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
        try:
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
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_users(self, start_cursor: Optional[str] = None, page_size: Optional[int] = None) -> ApiResponse:
        """
        Get a list of all users in the workspace.
        
        Args:
            start_cursor: Pagination cursor
            page_size: Number of results to return
            
        Returns:
            ApiResponse containing a list of users
        """
        try:
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

            print(f"User list: {user_list}")
            
            return self.prepare_response(user_list, "NotionUserList")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    def get_user(self, user_id: str) -> ApiResponse:
        """
        Get a specific user by ID.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            ApiResponse containing the user details
        """
        try:
            response = self.client.get_user(user_id)
            
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
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    def format_people_property(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Format user IDs into the proper format for the people property.
        
        Args:
            user_ids: List of user IDs
            
        Returns:
            List of properly formatted user objects for the people property
        """
        people = []
        for user_id in user_ids:
            # For each user ID, we need to determine if it's a person or bot
            try:
                user_response = self.client.get_user(user_id)
                
                if 'object' in user_response and user_response['object'] == 'error':
                    continue  # Skip this user if there's an error
                
                user_type = user_response.get('type')
                
                if user_type == 'person':
                    people.append({
                        "id": user_id
                    })
                elif user_type == 'bot':
                    people.append({
                        "id": user_id
                    })
            except Exception:
                # If we can't get the user, skip it
                continue
                
        return people

