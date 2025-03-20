from typing import Dict, Any, Optional, List
import os
from .client import TypeformClient
from .schema import (
    FormList, Form, ResponseList, WebhookList, Webhook, WorkspaceList,
    ApiResponse, GetFormsParams, GetFormParams, GetFormResponsesParams,
    CreateWebhookParams, GetWorkspacesParams, Workspace,
    CreateFormParams, UpdateFormParams, DeleteFormParams,
    DeleteWebhookParams, CreateWorkspaceParams
)
from ..common.component_handler import load_components, prepare_components_auto

class TypeformService:
    def __init__(self, client: TypeformClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "typeform"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_forms(self, params: GetFormsParams) -> ApiResponse:
        response = self.client.get_forms(
            search=params.search,
            page=params.page,
            page_size=params.page_size,
            workspace_id=params.workspace_id
        )
        
        # Convert the response to a FormList
        form_list = FormList(
            items=[Form(**form) for form in response.get('items', [])],
            page_count=response.get('page_count'),
            page_size=response.get('page_size'),
            total_items=response.get('total_items'),
            _links=response.get('_links')
        )
        
        return self.prepare_response(form_list, "FormList")
    
    def get_form(self, params: GetFormParams) -> ApiResponse:
        response = self.client.get_form(params.form_id)
        form = Form(**response)
        return self.prepare_response(form, "FormDetail")
    
    def get_form_responses(self, params: GetFormResponsesParams) -> ApiResponse:
        response = self.client.get_responses(
            form_id=params.form_id,
            page_size=params.page_size,
            since=params.since,
            until=params.until,
            after=params.after,
            before=params.before,
            completed=params.completed
        )
        
        # Process responses to map them to our schema
        responses = []
        for item in response.get('items', []):
            response_item = {
                'response_id': item.get('response_id'),
                'landing_id': item.get('landing_id'),
                'token': item.get('token'),
                'landed_at': item.get('landed_at'),
                'submitted_at': item.get('submitted_at'),
                'metadata': item.get('metadata'),
                'hidden': item.get('hidden'),
                'calculated': item.get('calculated'),
                'answers': item.get('answers')
            }
            responses.append(response_item)
            
        response_list = ResponseList(
            items=responses,
            page_count=response.get('page_count'),
            total_items=response.get('total_items'),
            _links=response.get('_links')
        )
        
        return self.prepare_response(response_list, "ResponseList")
    
    def get_webhooks(self, form_id: str) -> ApiResponse:
        response = self.client.get_webhooks(form_id)
        
        webhooks = [Webhook(
            id=webhook.get('id'),
            form_id=form_id,
            tag=webhook.get('tag'),
            url=webhook.get('url'),
            enabled=webhook.get('enabled', True),
            secret=webhook.get('secret'),
            verify_ssl=webhook.get('verify_ssl'),
            created_at=webhook.get('created_at'),
            updated_at=webhook.get('updated_at')
        ) for webhook in response.get('items', [])]
        
        webhook_list = WebhookList(items=webhooks)
        return self.prepare_response(webhook_list, "WebhookList")
    
    def create_webhook(self, params: CreateWebhookParams) -> ApiResponse:
        webhook_data = {
            "url": params.url,
            "enabled": params.enabled
        }
        
        if params.secret:
            webhook_data["secret"] = params.secret
            
        response = self.client.create_or_update_webhook(
            form_id=params.form_id,
            tag=params.tag,
            webhook_data=webhook_data
        )
        
        webhook = Webhook(
            id=response.get('id'),
            form_id=params.form_id,
            tag=params.tag,
            url=response.get('url'),
            enabled=response.get('enabled', True),
            secret=response.get('secret'),
            verify_ssl=response.get('verify_ssl'),
            created_at=response.get('created_at'),
            updated_at=response.get('updated_at')
        )
        
        return self.prepare_response(webhook, "Webhook")
    
    def get_workspaces(self, params: GetWorkspacesParams) -> ApiResponse:
        response = self.client.get_workspaces(
            search=params.search,
            page=params.page,
            page_size=params.page_size
        )
        
        items = response.get('items', [])
        if not isinstance(items, list):
            items = []
        
        processed_workspaces = []
        for workspace in items:
            if 'forms' in workspace and not isinstance(workspace['forms'], list):
                workspace = workspace.copy()
                workspace['forms'] = []
            processed_workspaces.append(workspace)
        
        workspace_list = WorkspaceList(
            items=[Workspace(**workspace) for workspace in processed_workspaces],
            page_count=response.get('page_count'),
            page_size=response.get('page_size'),
            total_items=response.get('total_items'),
            _links=response.get('_links')
        )
        
        return self.prepare_response(workspace_list, "WorkspaceList")
    
    def create_form(self, params: CreateFormParams) -> ApiResponse:
        form_data = params.model_dump(exclude_none=True)
        
        response = self.client.create_form(form_data)
        
        if 'forms' in response and not isinstance(response['forms'], list):
            response = response.copy()
            response['forms'] = []
        
        form = Form(**response)
        return self.prepare_response(form, "FormDetail")
    
    def update_form(self, params: UpdateFormParams) -> ApiResponse:
        form_id = params.form_id
        
        current_form = self.client.get_form(form_id)
        
        form_data = current_form.copy()
        update_data = params.model_dump(exclude={"form_id"}, exclude_none=True)
        
        for key, value in update_data.items():
            form_data[key] = value
        
        if "id" in form_data:
            del form_data["id"]
        
        response = self.client.update_form(form_id, form_data)
        
        if "fields" not in response and "id" in response:
            response = self.client.get_form(form_id)
        
        form = Form(**response)
        return self.prepare_response(form, "FormDetail")
    
    def delete_form(self, params: DeleteFormParams) -> ApiResponse:
        form_id = params.form_id
        response = self.client.delete_form(form_id)
        
        return self.prepare_response(response, "DeleteResult")
    
    def delete_webhook(self, params: DeleteWebhookParams) -> ApiResponse:
        form_id = params.form_id
        tag = params.tag
        response = self.client.delete_webhook(form_id, tag)
        
        return self.prepare_response(response, "DeleteResult")
    
    def create_workspace(self, params: CreateWorkspaceParams) -> ApiResponse:
        name = params.name
        response = self.client.create_workspace(name)
        
        if 'forms' in response and not isinstance(response['forms'], list):
            response = response.copy()
            response['forms'] = []
        
        workspace = Workspace(**response)
        return self.prepare_response(workspace, "WorkspaceDetail")
