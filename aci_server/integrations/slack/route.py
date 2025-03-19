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
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import os

router = APIRouter(prefix="/slack", tags=["slack"])

examples = ExamplesLoader()

async def get_slack_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'slack')

        if TokenService.is_token_expired(token_data):
            token_data = await SlackTokenRefresher.refresh(request, token_data)
        
        client = SlackClient(token_data['access_token'])
        apply_error_handler_to_client(client)
        service = SlackService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Slack service: {str(e)}")

@router.post("/list_channels", response_model=ApiResponse)
@schema(input_schema_class=ListChannelsParams, output_schema_class=ListChannelsResponse, examples=examples["/slack/list_channels"])
async def list_channels(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    validated_params = ListChannelsParams(**params)
    return service.list_channels(validated_params.cursor)

@router.post("/list_channel_members", response_model=ApiResponse)
@schema(input_schema_class=ListChannelMembersParams, output_schema_class=ListChannelMembersResponse, examples=examples["/slack/list_channel_members"])
async def list_channel_members(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    validated_params = ListChannelMembersParams(**params)
    return service.list_channel_members(validated_params.channel_id, validated_params.cursor)

@router.post("/list_direct_messages", response_model=ApiResponse)
@schema(input_schema_class=ListDirectMessagesParams, output_schema_class=ListDirectMessagesResponse, examples=examples["/slack/list_direct_messages"])
async def list_direct_messages(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    validated_params = ListDirectMessagesParams(**params)
    return service.list_direct_messages(validated_params.cursor)

@router.post("/post_message", response_model=ApiResponse)
@schema(input_schema_class=PostMessageParams, output_schema_class=PostMessageResponse, examples=examples["/slack/post_message"])
async def post_message(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    validated_params = PostMessageParams(**params)
    return service.post_message(validated_params.channel_id, validated_params.message.text)

@router.post("/send_dm", response_model=ApiResponse)
@schema(input_schema_class=SendDmParams, output_schema_class=SendDmResponse, examples=examples["/slack/send_dm"])
async def send_dm(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    validated_params = SendDmParams(**params)
    return service.send_dm(validated_params.message.user, validated_params.message.text)

@router.post("/reply_in_thread", response_model=ApiResponse)
@schema(input_schema_class=ReplyInThreadParams, output_schema_class=ReplyInThreadResponse, examples=examples["/slack/reply_in_thread"])
async def reply_in_thread(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    validated_params = ReplyInThreadParams(**params)
    return service.reply_in_thread(validated_params.channel_id, validated_params.thread_ts, validated_params.message.text)

@router.post("/list_thread_messages", response_model=ApiResponse)
@schema(input_schema_class=ListThreadMessagesParams, output_schema_class=ListThreadMessagesResponse, examples=examples["/slack/list_thread_messages"])
async def list_thread_messages(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    validated_params = ListThreadMessagesParams(**params)
    return service.list_thread_messages(validated_params.channel_id, validated_params.thread_ts, validated_params.cursor)

@router.post("/list_channel_messages", response_model=ApiResponse)
@schema(input_schema_class=ListChannelMessagesParams, output_schema_class=ListChannelMessagesResponse, examples=examples["/slack/list_channel_messages"])
async def list_channel_messages(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    validated_params = ListChannelMessagesParams(**params)
    return service.list_channel_messages(validated_params.channel_id, validated_params.cursor)

@router.post("/list_direct_messages_with_user", response_model=ApiResponse)
@schema(input_schema_class=ListDirectMessagesWithUserParams, output_schema_class=ListDirectMessagesWithUserResponse, examples=examples["/slack/list_direct_messages_with_user"])
async def list_direct_messages_with_user(
    params: Dict[str, Any] = Body(...),
    service: SlackService = Depends(get_slack_service)
):
    validated_params = ListDirectMessagesWithUserParams(**params)
    return service.list_direct_messages_with_user(validated_params.user, validated_params.cursor)

apply_error_handler_to_router(router)