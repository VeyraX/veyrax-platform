from typing import Optional, Dict, Any, List, Union
from .client import PostmanClient
from .schema import (
    ApiResponse, GetCollectionsParams, GetCollectionParams,
    UpdateCollectionParams, DeleteCollectionParams,
    CollectionListResponse, CollectionResponse, DeleteCollectionResponse,
    CollectionInfo, CollectionDetail, CollectionItem, CreateCollectionParams,
    GetEnvironmentsParams, GetEnvironmentParams, CreateEnvironmentParams,
    UpdateEnvironmentParams, DeleteEnvironmentParams, EnvironmentInfo, EnvironmentListResponse,
    EnvironmentResponse, DeleteEnvironmentResponse, ForkCollectionParams, ForkCollectionResponse,
    GetWorkspacesParams, GetWorkspaceParams, WorkspaceInfo, WorkspaceListResponse, WorkspaceResponse,
    CreateWorkspaceParams, DeleteWorkspaceParams, DeleteWorkspaceResponse, UpdateWorkspaceParams
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class PostmanService:
    def __init__(self, client: PostmanClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "postman"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_collections(self, params: Optional[GetCollectionsParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        
        if params and params.workspace_id:
            params_dict['workspace'] = params.workspace_id
        
        response = self.client.get_collections(params_dict)
        
        collections = []
        for item in response.get('collections', []):
            collection_info = CollectionInfo(
                id=item.get('id', ''),
                name=item.get('name', ''),
                uid=item.get('uid'),
                owner=item.get('owner'),
                schema=item.get('schema'),
                description=item.get('description'),
                forkLabel=item.get('forkLabel'),
                isPublic=item.get('isPublic'),
                createdAt=item.get('createdAt'),
                updatedAt=item.get('updatedAt')
            )
            collections.append(collection_info)
            
        collection_list = CollectionListResponse(collections=collections)
        
        return self.prepare_response(collection_list)

    def get_collection(self, collection_id: str, params: Optional[GetCollectionParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        if 'collection_id' in params_dict:
            del params_dict['collection_id']
            
        response = self.client.get_collection(collection_id, params_dict)
        
        collection_data = response.get('collection', {})
        info_data = collection_data.get('info', {})
        
        collection_info = CollectionInfo(
            id=info_data.get('id', ''),
            name=info_data.get('name', ''),
            uid=info_data.get('uid'),
            owner=info_data.get('owner'),
            schema=info_data.get('schema'),
            description=info_data.get('description'),
            forkLabel=info_data.get('forkLabel'),
            isPublic=info_data.get('isPublic'),
            createdAt=info_data.get('createdAt'),
            updatedAt=info_data.get('updatedAt')
        )
        
        items = self._process_collection_items(collection_data.get('item', []))
        
        collection_detail = CollectionDetail(
            info=collection_info,
            item=items,
            variable=collection_data.get('variable'),
            event=collection_data.get('event'),
            auth=collection_data.get('auth')
        )
        
        collection_response = CollectionResponse(collection=collection_detail)
        
        return self.prepare_response(collection_response)

    def _process_collection_items(self, items: List[Dict[str, Any]]) -> List[CollectionItem]:
        result = []
        for item in items:
            if not isinstance(item, dict):
                continue
                
            processed_item = CollectionItem(
                id=item.get('id'),
                name=item.get('name', ''),
                description=item.get('description'),
                request=item.get('request'),
                response=item.get('response')
            )
            
            if 'item' in item and isinstance(item['item'], list):
                processed_item.item = self._process_collection_items(item['item'])
                
            result.append(processed_item)
            
        return result

    def update_collection(self, params: UpdateCollectionParams) -> ApiResponse:
        collection_id = params.collection_id
        
        data = {"collection": params.collection}
        
        params_dict = params.dict(exclude_none=True)
        if 'collection_id' in params_dict:
            del params_dict['collection_id']
        if 'collection' in params_dict:
            del params_dict['collection']
        
        response = self.client.update_collection(collection_id, data, params_dict)
        
        collection_data = response.get('collection', {})
        
        collection_info = CollectionInfo(
            id=collection_data.get('id', ''),
            name=collection_data.get('name', ''),
            uid=collection_data.get('uid'),
            owner=collection_data.get('owner'),
            schema=collection_data.get('schema'),
            description=collection_data.get('description'),
            forkLabel=collection_data.get('forkLabel'),
            isPublic=collection_data.get('isPublic'),
            createdAt=collection_data.get('createdAt'),
            updatedAt=collection_data.get('updatedAt')
        )
        
        items = []
        
        collection_detail = CollectionDetail(
            info=collection_info,
            item=items,
            variable=None,
            event=None,
            auth=None
        )
        
        collection_response = CollectionResponse(collection=collection_detail)
        
        return self.prepare_response(collection_response)

    def delete_collection(self, params: DeleteCollectionParams) -> ApiResponse:
        collection_id = params.collection_id
        
        params_dict = params.dict(exclude_none=True)
        if 'collection_id' in params_dict:
            del params_dict['collection_id']
        
        response = self.client.delete_collection(collection_id, params_dict)
        
        delete_response = DeleteCollectionResponse(
            id=response.get('collection', {}).get('id', '') or response.get('id', ''),
            uid=response.get('collection', {}).get('uid') or response.get('uid'),
            name=response.get('collection', {}).get('name') or response.get('name')
        )
        
        return self.prepare_response(delete_response)

    def create_collection(self, params: CreateCollectionParams) -> ApiResponse:
        data = {"collection": params.collection}
        
        params_dict = params.dict(exclude_none=True)
        
        response = self.client.create_collection(data, params_dict)
        
        collection_data = response.get('collection', {})
        
        collection_info = CollectionInfo(
            id=collection_data.get('id', ''),
            name=collection_data.get('name', ''),
            uid=collection_data.get('uid'),
            owner=collection_data.get('owner'),
            schema=collection_data.get('schema'),
            description=collection_data.get('description'),
            forkLabel=collection_data.get('forkLabel'),
            isPublic=collection_data.get('isPublic'),
            createdAt=collection_data.get('createdAt'),
            updatedAt=collection_data.get('updatedAt')
        )
        
        items = []
        
        collection_detail = CollectionDetail(
            info=collection_info,
            item=items,
            variable=None,
            event=None,
            auth=None
        )
        
        collection_response = CollectionResponse(collection=collection_detail)
        
        return self.prepare_response(collection_response)

    def get_environments(self, params: Optional[GetEnvironmentsParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        response = self.client.get_environments(params_dict)
        
        environments = []
        for item in response.get('environments', []):
            environment_info = EnvironmentInfo(
                id=item.get('id', ''),
                name=item.get('name', ''),
                uid=item.get('uid'),
                owner=item.get('owner'),
                values=item.get('values'),
                isPublic=item.get('isPublic'),
                createdAt=item.get('createdAt'),
                updatedAt=item.get('updatedAt')
            )
            environments.append(environment_info)
            
        environment_list = EnvironmentListResponse(environments=environments)
        
        return self.prepare_response(environment_list)

    def get_environment(self, environment_id: str, params: Optional[GetEnvironmentParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        if 'environment_id' in params_dict:
            del params_dict['environment_id']
            
        response = self.client.get_environment(environment_id, params_dict)
        
        environment_data = response.get('environment', {})
        
        environment_info = EnvironmentInfo(
            id=environment_data.get('id', ''),
            name=environment_data.get('name', ''),
            uid=environment_data.get('uid'),
            owner=environment_data.get('owner'),
            values=environment_data.get('values'),
            isPublic=environment_data.get('isPublic'),
            createdAt=environment_data.get('createdAt'),
            updatedAt=environment_data.get('updatedAt')
        )
        
        environment_response = EnvironmentResponse(environment=environment_info)
        
        return self.prepare_response(environment_response)

    def create_environment(self, params: CreateEnvironmentParams) -> ApiResponse:
        data = {"environment": params.environment}
        
        params_dict = params.dict(exclude_none=True)
        if 'environment' in params_dict:
            del params_dict['environment']
        
        response = self.client.create_environment(data, params_dict)
        
        environment_data = response.get('environment', {})
        
        environment_info = EnvironmentInfo(
            id=environment_data.get('id', ''),
            name=environment_data.get('name', ''),
            uid=environment_data.get('uid'),
            owner=environment_data.get('owner'),
            values=environment_data.get('values'),
            isPublic=environment_data.get('isPublic'),
            createdAt=environment_data.get('createdAt'),
            updatedAt=environment_data.get('updatedAt')
        )
        
        environment_response = EnvironmentResponse(environment=environment_info)
        
        return self.prepare_response(environment_response)

    def update_environment(self, params: UpdateEnvironmentParams) -> ApiResponse:
        environment_id = params.environment_id
        
        data = {"environment": params.environment}
        
        params_dict = params.dict(exclude_none=True)
        if 'environment_id' in params_dict:
            del params_dict['environment_id']
        if 'environment' in params_dict:
            del params_dict['environment']
        
        response = self.client.update_environment(environment_id, data, params_dict)
        
        environment_data = response.get('environment', {})
        
        environment_info = EnvironmentInfo(
            id=environment_data.get('id', ''),
            name=environment_data.get('name', ''),
            uid=environment_data.get('uid'),
            owner=environment_data.get('owner'),
            values=environment_data.get('values'),
            isPublic=environment_data.get('isPublic'),
            createdAt=environment_data.get('createdAt'),
            updatedAt=environment_data.get('updatedAt')
        )
        
        environment_response = EnvironmentResponse(environment=environment_info)
        
        return self.prepare_response(environment_response)

    def delete_environment(self, params: DeleteEnvironmentParams) -> ApiResponse:
        environment_id = params.environment_id
        
        params_dict = params.dict(exclude_none=True)
        if 'environment_id' in params_dict:
            del params_dict['environment_id']
        
        response = self.client.delete_environment(environment_id, params_dict)
        
        delete_response = DeleteEnvironmentResponse(
            id=response.get('environment', {}).get('id', '') or response.get('id', ''),
            uid=response.get('environment', {}).get('uid') or response.get('uid'),
            name=response.get('environment', {}).get('name') or response.get('name')
        )
        
        return self.prepare_response(delete_response)

    def fork_collection(self, params: ForkCollectionParams) -> ApiResponse:
        collection_id = params.collection_id
        
        data = {}
        if params.label:
            data["label"] = params.label
        
        params_dict = params.dict(exclude_none=True)
        if 'collection_id' in params_dict:
            del params_dict['collection_id']
        if 'label' in params_dict:
            del params_dict['label']
        
        response = self.client.fork_collection(collection_id, data, params_dict)
        
        collection_data = response.get('collection', {})
        info_data = collection_data.get('info', {})
        
        collection_info = CollectionInfo(
            id=info_data.get('id', ''),
            name=info_data.get('name', ''),
            uid=info_data.get('uid'),
            owner=info_data.get('owner'),
            schema=info_data.get('schema'),
            description=info_data.get('description'),
            forkLabel=info_data.get('forkLabel'),
            isPublic=info_data.get('isPublic'),
            createdAt=info_data.get('createdAt'),
            updatedAt=info_data.get('updatedAt')
        )
        
        items = self._process_collection_items(collection_data.get('item', []))
        
        collection_detail = CollectionDetail(
            info=collection_info,
            item=items,
            variable=collection_data.get('variable'),
            event=collection_data.get('event'),
            auth=collection_data.get('auth')
        )
        
        fork_response = ForkCollectionResponse(collection=collection_detail)
        
        return self.prepare_response(fork_response)

    def get_workspaces(self, params: Optional[GetWorkspacesParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        response = self.client.get_workspaces(params_dict)
        
        workspaces = []
        for item in response.get('workspaces', []):
            workspace_info = WorkspaceInfo(
                id=item.get('id', ''),
                name=item.get('name', ''),
                type=item.get('type'),
                description=item.get('description'),
                visibility=item.get('visibility'),
                createdAt=item.get('createdAt'),
                updatedAt=item.get('updatedAt')
            )
            workspaces.append(workspace_info)
            
        workspace_list = WorkspaceListResponse(workspaces=workspaces)
        
        return self.prepare_response(workspace_list)

    def get_workspace(self, workspace_id: str, params: Optional[GetWorkspaceParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        if 'workspace_id' in params_dict:
            del params_dict['workspace_id']
        
        response = self.client.get_workspace(workspace_id, params_dict)
        
        workspace_data = response.get('workspace', {})
        
        workspace_info = WorkspaceInfo(
            id=workspace_data.get('id', ''),
            name=workspace_data.get('name', ''),
            type=workspace_data.get('type'),
            description=workspace_data.get('description'),
            visibility=workspace_data.get('visibility'),
            createdAt=workspace_data.get('createdAt'),
            updatedAt=workspace_data.get('updatedAt')
        )
        
        workspace_response = WorkspaceResponse(workspace=workspace_info)
        
        return self.prepare_response(workspace_response)

    def create_workspace(self, params: CreateWorkspaceParams) -> ApiResponse:
        data = {
            "workspace": {
                "name": params.name,
                "type": params.type
            }
        }
        
        if params.description:
            data["workspace"]["description"] = params.description
            
        if params.visibility:
            data["workspace"]["visibility"] = params.visibility
        
        params_dict = params.dict(exclude_none=True)
        for key in ['name', 'type', 'description', 'visibility']:
            if key in params_dict:
                del params_dict[key]
        
        response = self.client.create_workspace(data, params_dict)
        
        workspace_data = response.get('workspace', {})
        
        workspace_info = WorkspaceInfo(
            id=workspace_data.get('id', ''),
            name=workspace_data.get('name', ''),
            type=workspace_data.get('type'),
            description=workspace_data.get('description'),
            visibility=workspace_data.get('visibility'),
            createdAt=workspace_data.get('createdAt'),
            updatedAt=workspace_data.get('updatedAt')
        )
        
        workspace_response = WorkspaceResponse(workspace=workspace_info)
        
        return self.prepare_response(workspace_response)
    
    def update_workspace(self, params: UpdateWorkspaceParams) -> ApiResponse:
        workspace_id = params.workspace_id
        
        data = {"workspace": {}}
        
        if params.name:
            data["workspace"]["name"] = params.name
            
        if params.type:
            data["workspace"]["type"] = params.type
            
        if params.description:
            data["workspace"]["description"] = params.description
            
        if params.visibility:
            data["workspace"]["visibility"] = params.visibility
        
        params_dict = params.dict(exclude_none=True)
        for key in ['workspace_id', 'name', 'type', 'description', 'visibility']:
            if key in params_dict:
                del params_dict[key]
        
        response = self.client.update_workspace(workspace_id, data, params_dict)
        
        workspace_data = response.get('workspace', {})
        
        workspace_info = WorkspaceInfo(
            id=workspace_data.get('id', ''),
            name=workspace_data.get('name', ''),
            type=workspace_data.get('type'),
            description=workspace_data.get('description'),
            visibility=workspace_data.get('visibility'),
            createdAt=workspace_data.get('createdAt'),
            updatedAt=workspace_data.get('updatedAt')
        )
        
        workspace_response = WorkspaceResponse(workspace=workspace_info)
        
        return self.prepare_response(workspace_response)
        
    def delete_workspace(self, params: DeleteWorkspaceParams) -> ApiResponse:
        workspace_id = params.workspace_id
        
        params_dict = params.dict(exclude_none=True)
        if 'workspace_id' in params_dict:
            del params_dict['workspace_id']
        
        response = self.client.delete_workspace(workspace_id, params_dict)
        
        delete_response = DeleteWorkspaceResponse(
            id=response.get('workspace', {}).get('id', '') or response.get('id', ''),
            uid=response.get('workspace', {}).get('uid') or response.get('uid'),
            name=response.get('workspace', {}).get('name') or response.get('name')
        )
        
        return self.prepare_response(delete_response)
