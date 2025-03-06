from typing import Optional, Dict, Any, List, Union
from .client import OutlookClient
from .schema import (
    MessageList, Message, EventList, Event, EventCreate, 
    EventUpdate, Calendar, CalendarList, MessageFilters, 
    EventFilters, DraftMessage, ApiResponse
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
        
        return self.prepare_response(event_list, "OutlookCalendarEventCard")

    def get_event(self, event_id: str, calendar_id: Optional[str] = None) -> ApiResponse:
        event = self.client.get_event(event_id, calendar_id)
        
        event = self._convert_to_event(event)
        return self.prepare_response(event, "OutlookCalendarEventCard")

    def create_event(self, event: EventCreate, calendar_id: Optional[str] = None) -> ApiResponse:
        # Convert Pydantic model to dict for the client
        event_data = event.dict(exclude_none=True)
        response = self.client.create_event(event_data, calendar_id)
        created_event = self._convert_to_event(response)
        return self.prepare_response(created_event, "OutlookCalendarEventCard")

    def update_event(self, event_id: str, event: EventUpdate, 
                    calendar_id: Optional[str] = None) -> ApiResponse:
        event_data = event.dict(exclude_none=True)
        response = self.client.update_event(event_id, event_data, calendar_id)
        updated_event = self._convert_to_event(response)
        return self.prepare_response(updated_event, "OutlookCalendarEventCard")

    def delete_event(self, event_id: str, calendar_id: Optional[str] = None) -> None:
        self.client.delete_event(event_id, calendar_id)

    def _convert_to_message(self, item: Dict[str, Any]) -> Message:
        sender = None
        if 'from' in item and 'emailAddress' in item['from']:
            sender = item['from']['emailAddress'].get('address')
            
        recipient = None
        if 'toRecipients' in item and item['toRecipients']:
            recipients = []
            for to_recipient in item['toRecipients']:
                if 'emailAddress' in to_recipient:
                    recipients.append(to_recipient['emailAddress'].get('address'))
            if recipients:
                recipient = ', '.join(recipients)
        
        body_preview = item.get('bodyPreview', '')
        body = None
        if 'body' in item and 'content' in item['body']:
            body = item['body']['content']
            
        return Message(
            id=item.get('id', ''),
            subject=item.get('subject', ''),
            body_preview=body_preview,
            # body=body,
            sender=sender,
            recipient=recipient,
            date=item.get('createdDateTime'),
            web_link=item.get('webLink', ''),
            importance=item.get('importance'),
            is_read=item.get('isRead', False),
            categories=item.get('categories', [])
        )

    def _convert_to_event(self, item: Dict[str, Any]) -> Event:
        # Format datetime strings directly
        start_time = item['start']['dateTime'].split('.')[0] + 'Z'
        end_time = item['end']['dateTime'].split('.')[0] + 'Z'

        # Extract description from body content
        description = item.get('body', {}).get('content') if item.get('body') else None
        
        # Handle location as string
        location = None
        if item.get('location'):
            # Try different location formats
            if isinstance(item['location'], str):
                location = item['location']
            else:
                location = item['location'].get('displayName') or item['location'].get('locationUri')

        # Extract organizer information
        organizer = None
        if item.get('organizer'):
            org_email = item['organizer'].get('emailAddress', {})
            organizer = {
                "email": org_email.get('address'),
                "displayName": org_email.get('name')
            }

        # Process attendees
        attendees = []
        for attendee in item.get('attendees', []):
            email_info = attendee.get('emailAddress', {})
            attendees.append({
                "email": email_info.get('address'),
                "displayName": email_info.get('name'),
                "responseStatus": attendee.get('status', {}).get('response', 'none')
            })

        # Extract web link from Outlook's complex URL structure
        # TODO: looks like this is not working well, need to fix
        raw_url = item.get('webLink') or item.get('webUrl', '')
        # Clean up the Outlook URL to a direct calendar link
        web_link = raw_url.split('&exvsurl=1')[0].replace('owa/?itemid=', 'calendar/item/')

        return Event(
            id=item.get('id', ''),
            subject=item.get('subject', ''),
            body=item.get('body'),
            description=description,
            start=start_time,  # Direct string assignment
            end=end_time,      # Direct string assignment
            location=location,
            web_link=web_link,
            organizer=organizer,
            status=item.get('responseStatus', {}).get('response'),
            is_recurring=item.get('type') == 'seriesMaster',
            attendees=attendees
        )