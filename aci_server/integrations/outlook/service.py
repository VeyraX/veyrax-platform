from typing import Optional, Dict, Any, List, Union
from .client import OutlookClient
from .schema import (
    MessageList, Message, EventList, Event, EventCreate, 
    EventUpdate, Calendar, CalendarList, MessageFilters, 
    EventFilters, DraftMessage, Location, EmailAddress, Organizer, ApiResponse, EventTime
)
from datetime import datetime
import json
import os
from ..common.component_handler import load_components, prepare_components_auto


class OutlookService:
    def __init__(self, client: OutlookClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[Message, MessageList, EventList, CalendarList], component_name: str = None) -> ApiResponse:
        tool_name = "outlook"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    # Mail methods
    def get_messages(self, next_link: Optional[str] = None, filters: Optional[MessageFilters] = None) -> ApiResponse:
        params = {}
        
        if filters:
            filter_parts = []
            if filters.search:
                params['$search'] = f'"{filters.search}"'
            if filters.to:
                filter_parts.append(f"toRecipients/any(t: t/emailAddress/address eq '{filters.to}')")
            if filters.subject:
                filter_parts.append(f"contains(subject, '{filters.subject}')")
            if filters.after_date:
                filter_parts.append(f"createdDateTime ge {filters.after_date}")
            if filters.before_date:
                filter_parts.append(f"createdDateTime le {filters.before_date}")
            
            if filter_parts:
                params['$filter'] = ' and '.join(filter_parts)
            
            if filters.max_results:
                params['$top'] = filters.max_results

        response = self.client.list_messages(**params)
        
        messages = []
        for item in response.get('value', []):
            message = self._convert_to_message(item)
            messages.append(message)
            
        message_list = MessageList(
            messages=messages,
            next_link=response.get('@odata.nextLink')
        )
        
        return self.prepare_response(message_list, "OutlookMessageList")

    def get_message(self, message_id: str) -> ApiResponse:
        msg = self.client.get_message(message_id)
        message = self._convert_to_message(msg)
        return self.prepare_response(message, "OutlookMessageCard")

    def create_draft(self, draft: DraftMessage) -> ApiResponse:
        message_data = {
            "subject": draft.subject,
            "body": {
                "contentType": "HTML",
                "content": draft.body
            },
            "toRecipients": [{"emailAddress": {"address": recipient}} for recipient in draft.to_recipients]
        }
        
        response = self.client.create_draft(message_data)
        message = self._convert_to_message(response)
        return self.prepare_response(message, "OutlookMessageCard")

    def send_message(self, message_id: str) -> ApiResponse:
        message = self.client.get_message(message_id)
        
        message_data = {
            "subject": message.get("subject"),
            "body": message.get("body"),
            "toRecipients": message.get("toRecipients")
        }
        
        self.client.send_message(message_data)
        
        return {"status": "sent", "message_id": message_id}

    def delete_message(self, message_id: str) -> None:
        self.client.delete_message(message_id)

    # Calendar methods
    def list_calendars(self) -> ApiResponse:
        response = self.client.list_calendars()
        calendars = []
        
        for item in response.get('value', []):
            calendar = Calendar(
                id=item.get('id', ''),
                name=item.get('name', ''),
                color=item.get('color'),
                can_edit=item.get('canEdit', False),
                owner=item.get('owner')
            )
            calendars.append(calendar)
            
        calendar_list = CalendarList(calendars=calendars)
        return self.prepare_response(calendar_list)

    def list_events(self, next_link: Optional[str] = None, 
                   filters: Optional[EventFilters] = None) -> ApiResponse:
        params = {}
        calendar_id = None
        
        if filters:
            filter_parts = []
            if filters.calendar_id:
                calendar_id = filters.calendar_id
            if filters.search:
                filter_parts.append(f"contains(subject,'{filters.search}')")
            if filters.after_date:
                filter_parts.append(f"start/dateTime ge '{filters.after_date}'")
            if filters.before_date:
                filter_parts.append(f"end/dateTime le '{filters.before_date}'")
            
            if filter_parts:
                params['$filter'] = ' and '.join(filter_parts)
            
            if filters.max_results:
                params['$top'] = filters.max_results

        response = self.client.list_events(calendar_id, **params)
        events = []
        
        for item in response.get('value', []):
            event = self._convert_to_event(item)
            events.append(event)
            
        event_list = EventList(
            events=events,
            next_link=response.get('@odata.nextLink')
        )
        
        return self.prepare_response(event_list, "OutlookEventCard")

    def get_event(self, event_id: str, calendar_id: Optional[str] = None) -> ApiResponse:
        event = self.client.get_event(event_id, calendar_id)
        
        event = self._convert_to_event(event)
        return self.prepare_response(event, "OutlookEventCard")

    def create_event(self, event: EventCreate, calendar_id: Optional[str] = None) -> ApiResponse:
        event_data = event.dict(exclude_none=True)
        response = self.client.create_event(event_data, calendar_id)
        created_event = self._convert_to_event(response)
        return self.prepare_response(created_event, "OutlookEventCard")

    def update_event(self, event_id: str, event: EventUpdate, 
                    calendar_id: Optional[str] = None) -> ApiResponse:
        event_data = event.dict(exclude_none=True)
        response = self.client.update_event(event_id, event_data, calendar_id)
        updated_event = self._convert_to_event(response)
        return self.prepare_response(updated_event, "OutlookEventCard")

    def delete_event(self, event_id: str, calendar_id: Optional[str] = None) -> None:
        self.client.delete_event(event_id, calendar_id)

    def _convert_to_message(self, item: Dict[str, Any]) -> Message:
        from_address = None
        if 'from' in item and 'emailAddress' in item['from']:
            from_address = item['from']['emailAddress'].get('address')
            
        to_recipients = []
        if 'toRecipients' in item:
            for recipient in item['toRecipients']:
                if 'emailAddress' in recipient:
                    to_recipients.append(recipient['emailAddress'].get('address'))
        
        body_preview = item.get('bodyPreview', '')
        body = None
        if 'body' in item and 'content' in item['body']:
            body = item['body']['content']
            
        return Message(
            id=item.get('id', ''),
            subject=item.get('subject', ''),
            body_preview=body_preview,
            body=body,
            from_address=from_address,
            to_recipients=to_recipients,
            created_datetime=item.get('createdDateTime'),
            web_link=item.get('webLink', ''),
            importance=item.get('importance'),
            is_read=item.get('isRead', False),
            categories=item.get('categories', [])
        )

    def _convert_to_event(self, item: Dict[str, Any]) -> Event:
        start_time = None
        if 'start' in item and 'dateTime' in item['start']:
            start_time = EventTime(
                dateTime=item['start']['dateTime'],
                timeZone=item['start'].get('timeZone', 'UTC')
            )
            
        end_time = None
        if 'end' in item and 'dateTime' in item['end']:
            end_time = EventTime(
                dateTime=item['end']['dateTime'],
                timeZone=item['end'].get('timeZone', 'UTC')
            )
            
        location = None
        if 'location' in item and 'displayName' in item['location']:
            location = Location(
                displayName=item['location']['displayName'],
                address=item['location'].get('address', None),
                coordinates=item['location'].get('coordinates', None)
            )
            
        organizer = None
        if 'organizer' in item and 'emailAddress' in item['organizer']:
            email = EmailAddress(
                name=item['organizer']['emailAddress'].get('name'),
                address=item['organizer']['emailAddress'].get('address', '')
            )
            organizer = Organizer(emailAddress=email)
            
        body = None
        if 'body' in item and 'content' in item['body']:
            body = {
                'content': item['body']['content'],
                'contentType': item['body'].get('contentType', 'text')
            }
            
        return Event(
            id=item.get('id', ''),
            subject=item.get('subject', ''),
            body=body,
            start=start_time,
            end=end_time,
            location=location,
            web_link=item.get('webLink', ''),
            organizer=organizer,
            attendees=item.get('attendees')
        )