from typing import Dict, Any, List, Optional, Union
from .client import AirtableClient
from .schema import (
    ListRecordsParams, GetRecordParams, CreateRecordParams, CreateRecordsParams,
    UpdateRecordParams, UpdateRecordsParams, DeleteRecordParams, DeleteRecordsParams,
    UploadAttachmentParams, SyncCSVParams, CreateFieldParams, UpdateFieldParams,
    Record, RecordsList, DeletedRecord, DeletedRecordsList, UpsertResponse,
    SyncCSVResponse, FieldModel, ApiResponse, CreateTableParams, UpdateTableParams, TableModel,
    ListBasesParams, GetBaseSchemaParams, CreateBaseParams, BasesList, BaseSchema, BaseCreated,
    WebhooksList, WebhookCreated, WebhookPayloadsList, ListWebhooksParams, CreateWebhookParams, DeleteWebhookParams, ListWebhookPayloadsParams,
    UserInfo
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class AirtableService:
    def __init__(self, client: AirtableClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "airtable"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def list_records(self, params: ListRecordsParams) -> ApiResponse:
        query_params = self._process_list_params(params)
        response = self.client.list_records(
            params.base_id, 
            params.table_id_or_name,
            query_params
        )
        validated_data = RecordsList(**response)
        return self.prepare_response(validated_data, "RecordsList")

    def get_record(self, params: GetRecordParams) -> ApiResponse:
        query_params = {
            "cellFormat": params.cell_format,
            "returnFieldsByFieldId": params.return_fields_by_field_id
        }
        response = self.client.get_record(
            params.base_id,
            params.table_id_or_name,
            params.record_id,
            query_params
        )
        validated_data = Record(**response)
        return self.prepare_response(validated_data, "Record")

    def create_record(self, params: CreateRecordParams) -> ApiResponse:
        data = {
            "fields": params.fields,
            "typecast": params.typecast,
            "returnFieldsByFieldId": params.return_fields_by_field_id
        }
        response = self.client.create_records(
            params.base_id,
            params.table_id_or_name,
            data
        )
        validated_data = Record(**response)
        return self.prepare_response(validated_data, "Record")

    def create_records(self, params: CreateRecordsParams) -> ApiResponse:
        data = {
            "records": [record.model_dump() for record in params.records],
            "typecast": params.typecast,
            "returnFieldsByFieldId": params.return_fields_by_field_id
        }
        response = self.client.create_records(
            params.base_id,
            params.table_id_or_name,
            data
        )
        validated_data = RecordsList(**response)
        return self.prepare_response(validated_data, "RecordsList")

    def update_record(self, params: UpdateRecordParams) -> ApiResponse:
        data = {
            "fields": params.fields,
            "typecast": params.typecast,
            "returnFieldsByFieldId": params.return_fields_by_field_id
        }
        response = self.client.update_record(
            params.base_id,
            params.table_id_or_name,
            params.record_id,
            data,
            params.is_patch
        )
        validated_data = Record(**response)
        return self.prepare_response(validated_data, "Record")

    def update_records(self, params: UpdateRecordsParams) -> ApiResponse:
        data = {
            "records": [record.model_dump() for record in params.records],
            "typecast": params.typecast,
            "returnFieldsByFieldId": params.return_fields_by_field_id
        }
        
        if params.perform_upsert:
            data["performUpsert"] = params.perform_upsert
            response = self.client.update_records(
                params.base_id,
                params.table_id_or_name,
                data,
                params.is_patch
            )
            validated_data = UpsertResponse(**response)
        else:
            response = self.client.update_records(
                params.base_id,
                params.table_id_or_name,
                data,
                params.is_patch
            )
            validated_data = RecordsList(**response)
            
        return self.prepare_response(validated_data, "RecordsList")

    def delete_record(self, params: DeleteRecordParams) -> ApiResponse:
        response = self.client.delete_record(
            params.base_id,
            params.table_id_or_name,
            params.record_id
        )
        validated_data = DeletedRecord(**response)
        return self.prepare_response(validated_data, "DeletedRecord")

    def delete_records(self, params: DeleteRecordsParams) -> ApiResponse:
        response = self.client.delete_records(
            params.base_id,
            params.table_id_or_name,
            params.record_ids
        )
        validated_data = DeletedRecordsList(**response)
        return self.prepare_response(validated_data, "DeletedRecordsList")

    def upload_attachment(self, params: UploadAttachmentParams) -> ApiResponse:
        data = {
            "contentType": params.content_type,
            "file": params.file,
            "filename": params.filename
        }
        response = self.client.upload_attachment(
            params.base_id,
            params.record_id,
            params.attachment_field,
            data
        )
        validated_data = Record(**response)
        return self.prepare_response(validated_data, "Record")

    def sync_csv(self, params: SyncCSVParams) -> ApiResponse:
        response = self.client.sync_csv(
            params.base_id,
            params.table_id_or_name,
            params.api_endpoint_sync_id,
            params.csv_data
        )
        validated_data = SyncCSVResponse(**response)
        return self.prepare_response(validated_data, "SyncCSVResponse")
            
    # Field management methods
    def create_field(self, params: CreateFieldParams) -> ApiResponse:
        data = {
            "name": params.name,
            "type": params.type
        }
        
        if params.description:
            data["description"] = params.description
            
        if params.options:
            data["options"] = params.options
            
        response = self.client.create_field(
            params.base_id,
            params.table_id,
            data
        )
        
        validated_data = FieldModel(**response)
        return self.prepare_response(validated_data, "FieldModel")
        
    def update_field(self, params: UpdateFieldParams) -> ApiResponse:
        data = {}
        
        if params.name:
            data["name"] = params.name
            
        if params.description:
            data["description"] = params.description
            
        if not data:
            raise ValueError("At least one of name or description must be provided")
            
        response = self.client.update_field(
            params.base_id,
            params.table_id,
            params.column_id,
            data
        )
        
        validated_data = FieldModel(**response)
        return self.prepare_response(validated_data, "FieldModel")

    def _process_list_params(self, params: ListRecordsParams) -> Dict[str, Any]:
        query_params = {}
        
        if params.time_zone:
            query_params["timeZone"] = params.time_zone
        if params.user_locale:
            query_params["userLocale"] = params.user_locale
        if params.page_size:
            query_params["pageSize"] = params.page_size
        if params.max_records:
            query_params["maxRecords"] = params.max_records
        if params.offset:
            query_params["offset"] = params.offset
        if params.view:
            query_params["view"] = params.view
        if params.sort:
            query_params["sort"] = params.sort
        if params.filter_by_formula:
            query_params["filterByFormula"] = params.filter_by_formula
        if params.cell_format:
            query_params["cellFormat"] = params.cell_format
        if params.fields:
            query_params["fields"] = params.fields
        if params.return_fields_by_field_id is not None:
            query_params["returnFieldsByFieldId"] = params.return_fields_by_field_id
        if params.record_metadata:
            query_params["recordMetadata"] = params.record_metadata
            
        return query_params

    def create_table(self, params: CreateTableParams) -> ApiResponse:
        data = {
            "name": params.name,
            "fields": params.fields
        }
        
        if params.description:
            data["description"] = params.description
            
        response = self.client.create_table(
            params.base_id,
            data
        )
        
        validated_data = TableModel(**response)
        return self.prepare_response(validated_data, "TableModel")
        
    def update_table(self, params: UpdateTableParams) -> ApiResponse:
        data = {}
        
        if params.name:
            data["name"] = params.name
            
        if params.description is not None:  # Allow empty string to clear description
            data["description"] = params.description
            
        if not data:
            raise ValueError("At least one of name or description must be provided")
            
        response = self.client.update_table(
            params.base_id,
            params.table_id_or_name,
            data
        )
        
        validated_data = TableModel(**response)
        return self.prepare_response(validated_data, "TableModel")

    # Base management methods
    def list_bases(self, params: ListBasesParams) -> ApiResponse:
        response = self.client.list_bases(params.offset)
        validated_data = BasesList(**response)
        return self.prepare_response(validated_data, "BasesList")

    def get_base_schema(self, params: GetBaseSchemaParams) -> ApiResponse:
        response = self.client.get_base_schema(params.base_id, params.include)
        validated_data = BaseSchema(**response)
        return self.prepare_response(validated_data, "BaseSchema")

    def create_base(self, params: CreateBaseParams) -> ApiResponse:
        data = {
            "name": params.name,
            "workspaceId": params.workspace_id,
            "tables": params.tables
        }
        
        response = self.client.create_base(data)
        
        validated_data = BaseCreated(**response)
        return self.prepare_response(validated_data, "BaseCreated")

    # Webhook management methods
    def list_webhooks(self, params: ListWebhooksParams) -> ApiResponse:
        response = self.client.list_webhooks(params.base_id)
        validated_data = WebhooksList(**response)
        return self.prepare_response(validated_data, "WebhooksList")

    def create_webhook(self, params: CreateWebhookParams) -> ApiResponse:
        data = {
            "notificationUrl": params.notificationUrl,
            "specification": params.specification
        }
        
        data = {k: v for k, v in data.items() if v is not None}
        
        response = self.client.create_webhook(params.base_id, data)
        validated_data = WebhookCreated(**response)
        return self.prepare_response(validated_data, "WebhookCreated")

    def delete_webhook(self, params: DeleteWebhookParams) -> ApiResponse:
        response = self.client.delete_webhook(params.base_id, params.webhook_id)
        if not response:
            response = {"deleted": True}
        return self.prepare_response(response, "WebhookDeleted")

    def list_webhook_payloads(self, params: ListWebhookPayloadsParams) -> ApiResponse:
        query_params = {}
        if params.cursor is not None:
            query_params["cursor"] = params.cursor
        if params.limit is not None:
            query_params["limit"] = params.limit
        
        response = self.client.list_webhook_payloads(
            params.base_id,
            params.webhook_id,
            query_params
        )
        validated_data = WebhookPayloadsList(**response)
        return self.prepare_response(validated_data, "WebhookPayloadsList")

    # User info methods
    def get_user_info(self) -> ApiResponse:
        response = self.client.get_user_info()
        validated_data = UserInfo(**response)
        return self.prepare_response(validated_data, "UserInfo")
