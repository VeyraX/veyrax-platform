from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import (
    ApiResponse,
    GetCardsParams, GetCardParams, CreateCardParams, UpdateCardParams, DeleteCardParams,
    GetBoardsParams, GetBoardParams, GetListsParams, GetListParams,
    GetCardChecklistsParams, CreateChecklistParams, CreateChecklistItemParams,
    GetOrganizationsParams, GetOrganizationParams, GetOrganizationBoardsParams, GetOrganizationMembersParams,
    GetCardsResponse, GetCardResponse, CreateCardResponse, UpdateCardResponse, DeleteCardResponse,
    GetBoardsResponse, GetBoardResponse, GetListsResponse, GetListResponse,
    GetCardChecklistsResponse, CreateChecklistResponse, CreateChecklistItemResponse,
    GetOrganizationsResponse, GetOrganizationResponse, GetOrganizationBoardsResponse, GetOrganizationMembersResponse
)

from .service import TrelloService
from .client import TrelloClient
from ..common.auth import TokenService
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
import os
import pickle
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/trello", tags=["trello"])

examples = ExamplesLoader() 

async def get_trello_service(request: FastAPIRequest) -> TrelloService:
    try:
        token_data = await TokenService.get_user_token(request, 'trello')
        if not token_data:
            raise HTTPException(
                status_code=401,
                detail="No Trello token data found"
            )
            
        token = token_data.get('access_token')
        if not token:
            raise HTTPException(
                status_code=401,
                detail="No Trello token found"
            )
            
        client = TrelloClient(token)
        return TrelloService(client)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Trello service: {str(e)}"
        )

@router.post("/get_cards", response_model=ApiResponse)
@schema(input_schema_class=GetCardsParams, output_schema_class=GetCardsResponse, examples=examples["/trello/get_cards"])
async def get_cards(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetCardsParams(**params)
        return service.get_cards(
            board_id=validated_params.board_id,
            list_id=validated_params.list_id,
            limit=validated_params.limit
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetCardsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_card", response_model=ApiResponse)
@schema(input_schema_class=GetCardParams, output_schema_class=GetCardResponse, examples=examples["/trello/get_card"])
async def get_card(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetCardParams(**params)
        return service.get_card(validated_params.card_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetCardParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_card", response_model=ApiResponse)
@schema(input_schema_class=CreateCardParams, output_schema_class=CreateCardResponse, examples=examples["/trello/create_card"])
async def create_card(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = CreateCardParams(**params)
        return service.create_card(
            list_id=validated_params.list_id,
            name=validated_params.name,
            desc=validated_params.desc,
            pos=validated_params.pos,
            due=validated_params.due,
            label_ids=validated_params.label_ids
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateCardParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_card", response_model=ApiResponse)
@schema(input_schema_class=UpdateCardParams, output_schema_class=UpdateCardResponse, examples=examples["/trello/update_card"])
async def update_card(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = UpdateCardParams(**params)
        return service.update_card(
            card_id=validated_params.card_id,
            card_update=validated_params.card_update
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdateCardParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_card", response_model=ApiResponse)
@schema(input_schema_class=DeleteCardParams, output_schema_class=DeleteCardResponse, examples=examples["/trello/delete_card"])
async def delete_card(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = DeleteCardParams(**params)
        return service.delete_card(validated_params.card_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteCardParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_boards", response_model=ApiResponse)
@schema(input_schema_class=GetBoardsParams, output_schema_class=GetBoardsResponse, examples=examples["/trello/get_boards"])
async def get_boards(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetBoardsParams(**params)
        return service.get_boards(validated_params.member_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetBoardsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_board", response_model=ApiResponse)
@schema(input_schema_class=GetBoardParams, output_schema_class=GetBoardResponse, examples=examples["/trello/get_board"])
async def get_board(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetBoardParams(**params)
        return service.get_board(validated_params.board_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetBoardParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_lists", response_model=ApiResponse)
@schema(input_schema_class=GetListsParams, output_schema_class=GetListsResponse, examples=examples["/trello/get_lists"])
async def get_lists(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetListsParams(**params)
        return service.get_lists(validated_params.board_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetListsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_list", response_model=ApiResponse)
@schema(input_schema_class=GetListParams, output_schema_class=GetListResponse, examples=examples["/trello/get_list"])
async def get_list(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetListParams(**params)
        return service.get_list(validated_params.list_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetListParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_card_checklists", response_model=ApiResponse)
@schema(input_schema_class=GetCardChecklistsParams, output_schema_class=GetCardChecklistsResponse, examples=examples["/trello/get_card_checklists"])
async def get_card_checklists(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetCardChecklistsParams(**params)
        return service.get_card_checklists(validated_params.card_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetCardChecklistsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_checklist", response_model=ApiResponse)
@schema(input_schema_class=CreateChecklistParams, output_schema_class=CreateChecklistResponse, examples=examples["/trello/create_checklist"])
async def create_checklist(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = CreateChecklistParams(**params)
        return service.create_checklist(
            card_id=validated_params.card_id,
            name=validated_params.name
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateChecklistParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_checklist_item", response_model=ApiResponse)
@schema(input_schema_class=CreateChecklistItemParams, output_schema_class=CreateChecklistItemResponse, examples=examples["/trello/create_checklist_item"])
async def create_checklist_item(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = CreateChecklistItemParams(**params)
        return service.create_checklist_item(
            checklist_id=validated_params.checklist_id,
            name=validated_params.name,
            checked=validated_params.checked
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateChecklistItemParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_organizations", response_model=ApiResponse)
@schema(input_schema_class=GetOrganizationsParams, output_schema_class=GetOrganizationsResponse, examples=examples["/trello/get_organizations"])
async def get_organizations(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetOrganizationsParams(**params)
        return service.get_organizations(validated_params.member_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetOrganizationsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_organization", response_model=ApiResponse)
@schema(input_schema_class=GetOrganizationParams, output_schema_class=GetOrganizationResponse, examples=examples["/trello/get_organization"])
async def get_organization(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetOrganizationParams(**params)
        return service.get_organization(validated_params.org_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetOrganizationParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_organization_boards", response_model=ApiResponse)
@schema(input_schema_class=GetOrganizationBoardsParams, output_schema_class=GetOrganizationBoardsResponse, examples=examples["/trello/get_organization_boards"])
async def get_organization_boards(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetOrganizationBoardsParams(**params)
        return service.get_organization_boards(validated_params.org_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetOrganizationBoardsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_organization_members", response_model=ApiResponse)
@schema(input_schema_class=GetOrganizationMembersParams, output_schema_class=GetOrganizationMembersResponse, examples=examples["/trello/get_organization_members"])
async def get_organization_members(
    params: Dict[str, Any] = Body(...),
    service: TrelloService = Depends(get_trello_service)
):
    try:
        validated_params = GetOrganizationMembersParams(**params)
        return service.get_organization_members(validated_params.org_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetOrganizationMembersParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))