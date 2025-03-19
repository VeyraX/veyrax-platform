from fastapi import APIRouter, Depends, Body, HTTPException, Request
from typing import Dict, Any
from .schema import (
    ListDocsParams,
    ListPagesParams,
    CreatePageParams,
    UpdatePageParams,
    ExportPageParams,
    ApiResponse,
    PageList,
    Page,
    PageActionResponse,
    ExportStatus,
    ListTablesParams,
    ListColumnsParams,
    Table,
    TableList,
    Column,
    ColumnList,
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
    UserInfo,
    GetDocParams,
    GetPageParams,
    DeletePageParams,
    GetExportStatusParams,
    GetTableParams,
    GetColumnParams,
    GetRowParams,
    DeleteRowParams,
    PushButtonParams,
    GetFormulaParams,
    GetControlParams,
    WhoamiParams,
    UpdateRowParams
)
from .service import CodaService
from .client import CodaClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/coda", tags=["coda"])
examples = ExamplesLoader()

async def get_coda_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "coda")
        service = CodaService(CodaClient(api_key))
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coda service initialization failed: {str(e)}")

# Document endpoints
@router.post("/list_docs", response_model=ApiResponse)
@schema(
    input_schema_class=ListDocsParams,
    output_schema_class=PageList,
    examples=examples["/coda/list_docs"]
)
async def list_docs(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = ListDocsParams(**params)
    return service.list_docs(validated_params)

@router.post("/get_doc", response_model=ApiResponse)
@schema(
    input_schema_class=GetDocParams,
    output_schema_class=Page,
    examples=examples["/coda/get_doc"]
)
async def get_doc(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = GetDocParams(**params)
    return service.get_doc(validated_params.doc_id)

# Page endpoints
@router.post("/list_pages", response_model=ApiResponse)
@schema(
    input_schema_class=ListPagesParams,
    output_schema_class=PageList,
    examples=examples["/coda/list_pages"]
)
async def list_pages(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    validated_params = ListPagesParams(**params)
    return service.list_pages(doc_id, validated_params)

@router.post("/get_page", response_model=ApiResponse)
@schema(
    input_schema_class=GetPageParams,
    output_schema_class=Page,
    examples=examples["/coda/get_page"]
)
async def get_page(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = GetPageParams(**params)
    return service.get_page(validated_params.doc_id, validated_params.page_id)

@router.post("/create_page", response_model=ApiResponse)
@schema(
    input_schema_class=CreatePageParams,
    output_schema_class=PageActionResponse,
    examples=examples["/coda/create_page"]
)
async def create_page(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    validated_params = CreatePageParams(**params)
    return service.create_page(doc_id, validated_params)

@router.post("/update_page", response_model=ApiResponse)
@schema(
    input_schema_class=UpdatePageParams,
    output_schema_class=PageActionResponse,
    examples=examples["/coda/update_page"]
)
async def update_page(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    page_id = params.get("page_id")
    validated_params = UpdatePageParams(**params)
    return service.update_page(doc_id, page_id, validated_params)

@router.post("/delete_page", response_model=ApiResponse)
@schema(
    input_schema_class=DeletePageParams,
    output_schema_class=PageActionResponse,
    examples=examples["/coda/delete_page"]
)
async def delete_page(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = DeletePageParams(**params)
    return service.delete_page(validated_params.doc_id, validated_params.page_id)

@router.post("/export_page", response_model=ApiResponse)
@schema(
    input_schema_class=ExportPageParams,
    output_schema_class=ExportStatus,
    examples=examples["/coda/export_page"]
)
async def export_page(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    page_id = params.get("page_id")
    validated_params = ExportPageParams(**params)
    return service.export_page(doc_id, page_id, validated_params)

@router.post("/get_export_status", response_model=ApiResponse)
@schema(
    input_schema_class=GetExportStatusParams,
    output_schema_class=ExportStatus,
    examples=examples["/coda/get_export_status"]
)
async def get_export_status(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = GetExportStatusParams(**params)
    return service.get_export_status(validated_params.doc_id, validated_params.page_id, validated_params.request_id)

# Table endpoints
@router.post("/list_tables", response_model=ApiResponse)
@schema(
    input_schema_class=ListTablesParams,
    output_schema_class=TableList,
    examples=examples["/coda/list_tables"]
)
async def list_tables(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    validated_params = ListTablesParams(**params)
    return service.list_tables(doc_id, validated_params)

@router.post("/get_table", response_model=ApiResponse)
@schema(
    input_schema_class=GetTableParams,
    output_schema_class=Table,
    examples=examples["/coda/get_table"]
)
async def get_table(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = GetTableParams(**params)
    return service.get_table(validated_params.doc_id, validated_params.table_id)

# Column endpoints
@router.post("/list_columns", response_model=ApiResponse)
@schema(
    input_schema_class=ListColumnsParams,
    output_schema_class=ColumnList,
    examples=examples["/coda/list_columns"]
)
async def list_columns(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    table_id = params.get("table_id")
    validated_params = ListColumnsParams(**params)
    return service.list_columns(doc_id, table_id, validated_params)

@router.post("/get_column", response_model=ApiResponse)
@schema(
    input_schema_class=GetColumnParams,
    output_schema_class=Column,
    examples=examples["/coda/get_column"]
)
async def get_column(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = GetColumnParams(**params)
    return service.get_column(validated_params.doc_id, validated_params.table_id, validated_params.column_id)

# Row endpoints
@router.post("/list_rows", response_model=ApiResponse)
@schema(
    input_schema_class=ListRowsParams,
    output_schema_class=RowList,
    examples=examples["/coda/list_rows"]
)
async def list_rows(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    table_id = params.get("table_id")
    validated_params = ListRowsParams(**params)
    return service.list_rows(doc_id, table_id, validated_params)

@router.post("/get_row", response_model=ApiResponse)
@schema(
    input_schema_class=GetRowParams,
    output_schema_class=RowValue,
    examples=examples["/coda/get_row"]
)
async def get_row(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = GetRowParams(**params)
    return service.get_row(validated_params.doc_id, validated_params.table_id, validated_params.row_id)

@router.post("/create_rows", response_model=ApiResponse)
@schema(
    input_schema_class=CreateRowsRequest,
    output_schema_class=RowActionResponse,
    examples=examples["/coda/create_rows"]
)
async def create_rows(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    table_id = params.get("table_id")
    validated_params = CreateRowsRequest(**params)
    return service.create_rows(doc_id, table_id, validated_params)

@router.post("/delete_rows", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteRowsRequest,
    output_schema_class=RowActionResponse,
    examples=examples["/coda/delete_rows"]
)
async def delete_rows(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    table_id = params.get("table_id")
    validated_params = DeleteRowsRequest(**params)
    return service.delete_rows(doc_id, table_id, validated_params)

@router.post("/delete_row", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteRowParams,
    output_schema_class=RowActionResponse,
    examples=examples["/coda/delete_row"]
)
async def delete_row(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = DeleteRowParams(**params)
    return service.delete_row(validated_params.doc_id, validated_params.table_id, validated_params.row_id)

@router.post("/push_button", response_model=ApiResponse)
@schema(
    input_schema_class=PushButtonParams,
    output_schema_class=RowActionResponse,
    examples=examples["/coda/push_button"]
)
async def push_button(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = PushButtonParams(**params)
    return service.push_button(validated_params.doc_id, validated_params.table_id, validated_params.row_id, validated_params.column_id)

# Formula endpoints
@router.post("/list_formulas", response_model=ApiResponse)
@schema(
    input_schema_class=ListFormulasParams,
    output_schema_class=FormulaList,
    examples=examples["/coda/list_formulas"]
)
async def list_formulas(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    validated_params = ListFormulasParams(**params)
    return service.list_formulas(doc_id, validated_params)

@router.post("/get_formula", response_model=ApiResponse)
@schema(
    input_schema_class=GetFormulaParams,
    output_schema_class=Formula,
    examples=examples["/coda/get_formula"]
)
async def get_formula(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = GetFormulaParams(**params)
    return service.get_formula(validated_params.doc_id, validated_params.formula_id)

# Control endpoints
@router.post("/list_controls", response_model=ApiResponse)
@schema(
    input_schema_class=ListControlsParams,
    output_schema_class=ControlList,
    examples=examples["/coda/list_controls"]
)
async def list_controls(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    doc_id = params.get("doc_id")
    validated_params = ListControlsParams(**params)
    return service.list_controls(doc_id, validated_params)

@router.post("/get_control", response_model=ApiResponse)
@schema(
    input_schema_class=GetControlParams,
    output_schema_class=Control,
    examples=examples["/coda/get_control"]
)
async def get_control(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = GetControlParams(**params)
    return service.get_control(validated_params.doc_id, validated_params.control_id)

# User endpoints
@router.post("/whoami", response_model=ApiResponse)
@schema(
    input_schema_class=WhoamiParams,
    output_schema_class=UserInfo,
    examples=examples["/coda/whoami"]
)
async def whoami(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    return service.get_whoami()

@router.post("/update_row", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateRowParams,
    output_schema_class=RowActionResponse,
    examples=examples["/coda/update_row"]
)
async def update_row(
    params: Dict[str, Any] = Body(...),
    service: CodaService = Depends(get_coda_service)
):
    validated_params = UpdateRowParams(**params)
    return service.update_row(validated_params.doc_id, validated_params.table_id, validated_params.row_id, validated_params.row)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key", "")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = CodaClient(api_key)
        # Test the API key with a simple operation
        test_params = {"limit": 1}
        client.list_docs(test_params)
        
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}
    
apply_error_handler_to_router(router)