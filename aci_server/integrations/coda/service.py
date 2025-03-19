from typing import Dict, Any, Optional, List, Union
from .client import CodaClient
from .schema import (
    ApiResponse, 
    Page, 
    PageList, 
    PageActionResponse,
    ExportStatus,
    ListPagesParams,
    CreatePageParams,
    UpdatePageParams,
    ExportPageParams,
    ListDocsParams,
    Table,
    TableList,
    Column,
    ColumnList,
    ListTablesParams,
    ListColumnsParams,
    RowValue,
    RowList,
    RowActionResponse,
    ListRowsParams,
    CreateRowsRequest,
    UpdateRowsRequest,
    DeleteRowsRequest,
    Formula,
    FormulaList,
    ListFormulasParams,
    Control,
    ControlList,
    ListControlsParams,
    UserInfo
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class CodaService:
    def __init__(self, client: CodaClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "coda"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def list_docs(self, params: ListDocsParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.list_docs(processed_params)
        return self.prepare_response(response, "CodaDocList")
        
    def get_doc(self, doc_id: str) -> ApiResponse:
        response = self.client.get_doc(doc_id)
        return self.prepare_response(response, "CodaDocDetail")

    def list_pages(self, doc_id: str, params: ListPagesParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.list_pages(doc_id, processed_params)
        page_list = PageList(**response)
        return self.prepare_response(page_list, "CodaPageList")

    def get_page(self, doc_id: str, page_id: str) -> ApiResponse:
        response = self.client.get_page(doc_id, page_id)
        page = Page(**response)
        return self.prepare_response(page, "CodaPageDetail")
        
    def create_page(self, doc_id: str, params: CreatePageParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.create_page(doc_id, processed_params)
        action_response = PageActionResponse(**response)
        return self.prepare_response(action_response, "CodaActionResponse")
        
    def update_page(self, doc_id: str, page_id: str, params: UpdatePageParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.update_page(doc_id, page_id, processed_params)
        action_response = PageActionResponse(**response)
        return self.prepare_response(action_response, "CodaActionResponse")
        
    def delete_page(self, doc_id: str, page_id: str) -> ApiResponse:
        response = self.client.delete_page(doc_id, page_id)
        action_response = PageActionResponse(**response)
        return self.prepare_response(action_response, "CodaActionResponse")
        
    def export_page(self, doc_id: str, page_id: str, params: ExportPageParams) -> ApiResponse:
        processed_params = {
            "outputFormat": params.output_format
        }
        response = self.client.export_page(doc_id, page_id, processed_params)
        export_status = ExportStatus(**response)
        return self.prepare_response(export_status, "CodaExportStatus")
        
    def get_export_status(self, doc_id: str, page_id: str, request_id: str) -> ApiResponse:
        response = self.client.get_export_status(doc_id, page_id, request_id)
        export_status = ExportStatus(**response)
        return self.prepare_response(export_status, "CodaExportStatus")

    # Table methods
    def list_tables(self, doc_id: str, params: ListTablesParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.list_tables(doc_id, processed_params)
        table_list = TableList(**response)
        return self.prepare_response(table_list, "CodaTableList")
    
    def get_table(self, doc_id: str, table_id: str) -> ApiResponse:
        response = self.client.get_table(doc_id, table_id)
        table = Table(**response)
        return self.prepare_response(table, "CodaTableDetail")
    
    # Column methods
    def list_columns(self, doc_id: str, table_id: str, params: ListColumnsParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.list_columns(doc_id, table_id, processed_params)
        column_list = ColumnList(**response)
        return self.prepare_response(column_list, "CodaColumnList")
    
    def get_column(self, doc_id: str, table_id: str, column_id: str) -> ApiResponse:
        response = self.client.get_column(doc_id, table_id, column_id)
        column = Column(**response)
        return self.prepare_response(column, "CodaColumnDetail")

    # Row methods
    def list_rows(self, doc_id: str, table_id: str, params: ListRowsParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.list_rows(doc_id, table_id, processed_params)
        row_list = RowList(**response)
        return self.prepare_response(row_list, "CodaRowList")
    
    def get_row(self, doc_id: str, table_id: str, row_id: str) -> ApiResponse:
        response = self.client.get_row(doc_id, table_id, row_id)
        row = RowValue(**response)
        return self.prepare_response(row, "CodaRowDetail")
    
    def create_rows(self, doc_id: str, table_id: str, params: CreateRowsRequest) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.create_rows(doc_id, table_id, processed_params)
        action_response = RowActionResponse(**response)
        return self.prepare_response(action_response, "CodaRowActionResponse")
    
    def delete_rows(self, doc_id: str, table_id: str, params: DeleteRowsRequest) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        if "row_ids" in processed_params and "rowIds" not in processed_params:
            processed_params["rowIds"] = processed_params.pop("row_ids")
        
        response = self.client.delete_rows(doc_id, table_id, processed_params)
        action_response = RowActionResponse(**response)
        return self.prepare_response(action_response, "CodaRowActionResponse")
    
    def delete_row(self, doc_id: str, table_id: str, row_id: str) -> ApiResponse:
        response = self.client.delete_row(doc_id, table_id, row_id)
        action_response = RowActionResponse(**response)
        return self.prepare_response(action_response, "CodaRowActionResponse")
    
    def push_button(self, doc_id: str, table_id: str, row_id: str, column_id: str) -> ApiResponse:
        response = self.client.push_button(doc_id, table_id, row_id, column_id)
        action_response = RowActionResponse(**response)
        return self.prepare_response(action_response, "CodaButtonPushResponse")

    # Formula methods
    def list_formulas(self, doc_id: str, params: ListFormulasParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.list_formulas(doc_id, processed_params)
        formula_list = FormulaList(**response)
        return self.prepare_response(formula_list, "CodaFormulaList")
    
    def get_formula(self, doc_id: str, formula_id: str) -> ApiResponse:
        response = self.client.get_formula(doc_id, formula_id)
        formula = Formula(**response)
        return self.prepare_response(formula, "CodaFormulaDetail")
    
    # Control methods
    def list_controls(self, doc_id: str, params: ListControlsParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.list_controls(doc_id, processed_params)
        control_list = ControlList(**response)
        return self.prepare_response(control_list, "CodaControlList")
    
    def get_control(self, doc_id: str, control_id: str) -> ApiResponse:
        response = self.client.get_control(doc_id, control_id)
        control = Control(**response)
        return self.prepare_response(control, "CodaControlDetail")
    
    # User methods
    def get_whoami(self) -> ApiResponse:
        response = self.client.get_whoami()
        user_info = UserInfo(**response)
        return self.prepare_response(user_info, "CodaUserInfo")

    def update_row(self, doc_id: str, table_id: str, row_id: str, row_data: Dict[str, Any]) -> ApiResponse:
        response = self.client.update_row(doc_id, table_id, row_id, row_data)
        action_response = RowActionResponse(**response)
        return self.prepare_response(action_response, "CodaRowActionResponse")
