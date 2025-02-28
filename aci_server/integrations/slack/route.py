from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import (
    ChannelList, ChannelMemberList, MessageList, 
    Message, DirectMessage, ThreadMessage,
    ListChannelsParams, ListChannelMembersParams, ListDirectMessagesParams,
    PostMessageParams, SendDmParams, ReplyInThreadParams, ListThreadMessagesParams,
    ListChannelMessagesParams, ListDirectMessagesWithUserParams,
    ApiResponse, ListChannelsResponse, ListChannelMembersResponse, ListDirectMessagesResponse,
    PostMessageResponse, SendDmResponse, ReplyInThreadResponse, ListThreadMessagesResponse,
    ListChannelMessagesResponse, ListDirectMessagesWithUserResponse
)
from .service import SlackService
from .client import SlackClient
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.auth import TokenService, SlackTokenRefresher
from pydantic import ValidationError
from ..common.utils import format_validation_error
import os

router = APIRouter(prefix="/slack", tags=["slack"])

async def get_slack_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'slack')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await SlackTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"Failed to refresh token: {str(e)}")
        
        client = SlackClient(token_data['access_token'])
        return SlackService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Slack service: {str(e)}")

@router.post("/list_channels", response_model=ApiResponse)
@schema(input_schema_class=ListChannelsParams, output_schema_class=ListChannelsResponse)
async def list_channels(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    try:
        validated_params = ListChannelsParams(**params)
        return service.list_channels(validated_params.cursor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListChannelsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_channel_members", response_model=ApiResponse)
@schema(input_schema_class=ListChannelMembersParams, output_schema_class=ListChannelMembersResponse)
async def list_channel_members(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    try:
        validated_params = ListChannelMembersParams(**params)
        return service.list_channel_members(validated_params.channel_id, validated_params.cursor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListChannelMembersParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_direct_messages", response_model=ApiResponse)
@schema(input_schema_class=ListDirectMessagesParams, output_schema_class=ListDirectMessagesResponse)
async def list_direct_messages(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    try:
        validated_params = ListDirectMessagesParams(**params)
        return service.list_direct_messages(validated_params.cursor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListDirectMessagesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/post_message", response_model=ApiResponse)
@schema(input_schema_class=PostMessageParams, output_schema_class=PostMessageResponse)
async def post_message(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    try:
        validated_params = PostMessageParams(**params)
        return service.post_message(validated_params.channel_id, validated_params.message.text)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'PostMessageParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send_dm", response_model=ApiResponse)
@schema(input_schema_class=SendDmParams, output_schema_class=SendDmResponse)
async def send_dm(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    try:
        validated_params = SendDmParams(**params)
        return service.send_dm(validated_params.message.user_id, validated_params.message.text)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SendDmParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reply_in_thread", response_model=ApiResponse)
@schema(input_schema_class=ReplyInThreadParams, output_schema_class=ReplyInThreadResponse)
async def reply_in_thread(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    try:
        validated_params = ReplyInThreadParams(**params)
        return service.reply_in_thread(validated_params.channel_id, validated_params.thread_ts, validated_params.message.text)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ReplyInThreadParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_thread_messages", response_model=ApiResponse)
@schema(input_schema_class=ListThreadMessagesParams, output_schema_class=ListThreadMessagesResponse)
async def list_thread_messages(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    try:
        validated_params = ListThreadMessagesParams(**params)
        return service.list_thread_messages(validated_params.channel_id, validated_params.thread_ts, validated_params.cursor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListThreadMessagesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_channel_messages", response_model=ApiResponse)
@schema(input_schema_class=ListChannelMessagesParams, output_schema_class=ListChannelMessagesResponse)
async def list_channel_messages(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    try:
        validated_params = ListChannelMessagesParams(**params)
        return service.list_channel_messages(validated_params.channel_id, validated_params.cursor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListChannelMessagesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_direct_messages_with_user", response_model=ApiResponse)
@schema(input_schema_class=ListDirectMessagesWithUserParams, output_schema_class=ListDirectMessagesWithUserResponse)
async def list_direct_messages_with_user(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    try:
        validated_params = ListDirectMessagesWithUserParams(**params)
        return service.list_direct_messages_with_user(validated_params.user_id, validated_params.cursor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListDirectMessagesWithUserParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))