from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import (
    ApiResponse, GetSpreadsheetParams, GetSpreadsheetValuesParams,
    GetSpreadsheetValuesBatchParams, UpdateSpreadsheetValuesParams,
    AppendSpreadsheetValuesParams, ClearSpreadsheetValuesParams,
    CreateSpreadsheetParams, AddSheetParams, DeleteSheetParams,
    ListSpreadsheetsParams, GetSpreadsheetResponse, GetSpreadsheetValuesResponse,
    GetSpreadsheetValuesBatchResponse, UpdateSpreadsheetValuesResponse,
    AppendSpreadsheetValuesResponse, ClearSpreadsheetValuesResponse,
    CreateSpreadsheetResponse, AddSheetResponse, DeleteSheetResponse,
    ListSpreadsheetsResponse,
    SearchSpreadsheetParams, GetFormulasParams, AddFormulaParams,
    SearchSpreadsheetResponse, GetFormulasResponse, AddFormulaResponse
)
from .service import GoogleSheetsService
from .client import GoogleSheetsClient
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.input_schema_decorator import schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/google_sheets", tags=["google_sheets"])

examples = ExamplesLoader()

async def get_sheets_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'google-sheets')

        if TokenService.is_token_expired(token_data):
            try:
                token_data = await GoogleTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
            
        creds = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=token_data['scopes'].split(',')
        )
        
        client = GoogleSheetsClient(creds)
        apply_error_handler_to_client(client)
        service = GoogleSheetsService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Google Sheets service: {str(e)}")


@router.post("/get_spreadsheet", response_model=ApiResponse)
@schema(input_schema_class=GetSpreadsheetParams, output_schema_class=GetSpreadsheetResponse, examples=examples["/google_sheets/get_spreadsheet"])
async def get_spreadsheet(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = GetSpreadsheetParams(**params)
    return service.get_spreadsheet(validated_params.spreadsheet_id)

@router.post("/get_spreadsheet_values", response_model=ApiResponse)
@schema(input_schema_class=GetSpreadsheetValuesParams, output_schema_class=GetSpreadsheetValuesResponse, examples=examples["/google_sheets/get_spreadsheet_values"])
async def get_spreadsheet_values(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = GetSpreadsheetValuesParams(**params)
    return service.get_spreadsheet_values(validated_params.spreadsheet_id, validated_params.range)

@router.post("/get_spreadsheet_values_batch", response_model=ApiResponse)
@schema(input_schema_class=GetSpreadsheetValuesBatchParams, output_schema_class=GetSpreadsheetValuesBatchResponse, examples=examples["/google_sheets/get_spreadsheet_values_batch"])
async def get_spreadsheet_values_batch(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = GetSpreadsheetValuesBatchParams(**params)
    return service.get_spreadsheet_values_batch(validated_params.spreadsheet_id, validated_params.ranges)

@router.post("/update_spreadsheet_values", response_model=ApiResponse)
@schema(input_schema_class=UpdateSpreadsheetValuesParams, output_schema_class=UpdateSpreadsheetValuesResponse, examples=examples["/google_sheets/update_spreadsheet_values"])
async def update_spreadsheet_values(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = UpdateSpreadsheetValuesParams(**params)
    return service.update_spreadsheet_values(
        validated_params.spreadsheet_id, 
        validated_params.range, 
        validated_params.values, 
        validated_params.value_input_option
    )

@router.post("/append_spreadsheet_values", response_model=ApiResponse)
@schema(input_schema_class=AppendSpreadsheetValuesParams, output_schema_class=AppendSpreadsheetValuesResponse, examples=examples["/google_sheets/append_spreadsheet_values"])
async def append_spreadsheet_values(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = AppendSpreadsheetValuesParams(**params)
    return service.append_spreadsheet_values(
        validated_params.spreadsheet_id, 
        validated_params.range, 
        validated_params.values, 
        validated_params.value_input_option
    )

@router.post("/clear_spreadsheet_values", response_model=ApiResponse)
@schema(input_schema_class=ClearSpreadsheetValuesParams, output_schema_class=ClearSpreadsheetValuesResponse, examples=examples["/google_sheets/clear_spreadsheet_values"])
async def clear_spreadsheet_values(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = ClearSpreadsheetValuesParams(**params)
    return service.clear_spreadsheet_values(validated_params.spreadsheet_id, validated_params.range)

@router.post("/create_spreadsheet", response_model=ApiResponse)
@schema(input_schema_class=CreateSpreadsheetParams, output_schema_class=CreateSpreadsheetResponse, examples=examples["/google_sheets/create_spreadsheet"])
async def create_spreadsheet(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = CreateSpreadsheetParams(**params)
    return service.create_spreadsheet(validated_params.title)

@router.post("/add_sheet", response_model=ApiResponse)
@schema(input_schema_class=AddSheetParams, output_schema_class=AddSheetResponse, examples=examples["/google_sheets/add_sheet"])
async def add_sheet(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = AddSheetParams(**params)
    return service.add_sheet(validated_params.spreadsheet_id, validated_params.sheet_title)

@router.post("/delete_sheet", response_model=ApiResponse)
@schema(input_schema_class=DeleteSheetParams, output_schema_class=DeleteSheetResponse, examples=examples["/google_sheets/delete_sheet"])
async def delete_sheet(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = DeleteSheetParams(**params)
    return service.delete_sheet(validated_params.spreadsheet_id, validated_params.sheet_id)

@router.post("/search_spreadsheet", response_model=ApiResponse)
@schema(input_schema_class=SearchSpreadsheetParams, output_schema_class=SearchSpreadsheetResponse, examples=examples["/google_sheets/search_spreadsheet"])
async def search_spreadsheet(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = SearchSpreadsheetParams(**params)
    return service.search_in_spreadsheet(
        validated_params.spreadsheet_id, 
        validated_params.search_term,
        validated_params.ranges,
        validated_params.case_sensitive
    )

@router.post("/get_formulas", response_model=ApiResponse)
@schema(input_schema_class=GetFormulasParams, output_schema_class=GetFormulasResponse, examples=examples["/google_sheets/get_formulas"])
async def get_formulas(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = GetFormulasParams(**params)
    return service.get_formulas(validated_params.spreadsheet_id, validated_params.range)

@router.post("/add_formula", response_model=ApiResponse)
@schema(input_schema_class=AddFormulaParams, output_schema_class=AddFormulaResponse, examples=examples["/google_sheets/add_formula"])
async def add_formula(
    params: Dict[str, Any] = Body(...),
    service: GoogleSheetsService = Depends(get_sheets_service)
):
    validated_params = AddFormulaParams(**params)
    return service.add_formula(
        validated_params.spreadsheet_id, 
        validated_params.range,
        validated_params.formula
    )

apply_error_handler_to_router(router)
