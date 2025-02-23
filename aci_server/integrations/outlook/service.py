from typing import Optional, Dict, Any
from .client import OutlookClient
from .schema import (
    MessageList, Message, EventList, Event, EventCreate, 
    EventUpdate, Calendar, CalendarList, MessageFilters, 
    EventFilters, DraftMessage, Location, EmailAddress, Organizer
)
from datetime import datetime
import json

class OutlookService:
    def __init__(self, client: OutlookClient):
        self.client = client

    # Mail methods
    def get_messages(self, next_link: Optional[str] = None, filters: Optional[MessageFilters] = None) -> MessageList:
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
        
        messages = [{
            'id': msg['id'],
            'subject': msg.get('subject'),
            'body_preview': msg.get('bodyPreview', ''),
            'body': msg.get('body', {}).get('content'),
            'from_address': msg.get('from', {}).get('emailAddress', {}).get('address'),
            'to_recipients': [r['emailAddress']['address'] for r in msg.get('toRecipients', [])],
            'created_datetime': msg['createdDateTime'],
            'web_link': msg.get('webLink', '')
        } for msg in response.get('value', [])]

        return MessageList(
            messages=messages,
            next_link=response.get('@odata.nextLink')
        )

    def get_message(self, message_id: str) -> Message:
        msg = self.client.get_message(message_id)
        return Message(
            id=msg['id'],
            subject=msg.get('subject'),
            body_preview=msg.get('bodyPreview', ''),
            body=msg.get('body', {}).get('content'),
            from_address=msg.get('from', {}).get('emailAddress', {}).get('address'),
            to_recipients=[r['emailAddress']['address'] for r in msg.get('toRecipients', [])],
            created_datetime=msg['createdDateTime'],
            web_link=msg.get('webLink', ''),
            importance=msg.get('importance'),
            is_read=msg.get('isRead', False),
            categories=msg.get('categories', [])
        )

    def create_draft(self, draft: DraftMessage) -> Message:
        message_data = {
            "subject": draft.subject,
            "body": {
                "contentType": "HTML",
                "content": draft.body
            },
            "toRecipients": [{"emailAddress": {"address": recipient}} for recipient in draft.to_recipients]
        }
        
        response = self.client.create_draft(message_data)
        return self.get_message(response['id'])

    def send_message(self, message_id: str) -> Dict[str, Any]:
        message = self.client.get_message(message_id)
        
        message_data = {
            "subject": message.get("subject"),
            "body": message.get("body"),
            "toRecipients": message.get("toRecipients")
        }
        
        self.client.send_message(message_data)
        
        return {
            "status": "sent",
            "message_id": message_id,
            "subject": message.get("subject"),
            "to": [r['emailAddress']['address'] for r in message.get("toRecipients", [])],
            "body": message.get("body", {}).get("content"),
            "webLink": message.get("webLink", '')
        }

    def delete_message(self, message_id: str) -> None:
        self.client.delete_message(message_id)

    # Calendar methods
    def list_calendars(self) -> CalendarList:
        response = self.client.list_calendars()
        calendars = []
        
        for cal in response.get('value', []):
            calendars.append(Calendar(
                id=cal['id'],
                name=cal['name'],
                color=cal.get('color'),
                can_edit=cal.get('canEdit', False),
                owner=cal.get('owner')
            ))
            
        return CalendarList(calendars=calendars)

    def list_events(self, next_link: Optional[str] = None, 
                   filters: Optional[EventFilters] = None) -> EventList:
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
        
        for event in response.get('value', []):
            location = None
            if event.get('location'):
                loc_data = event['location']
                coordinates = None
                if isinstance(loc_data.get('coordinates'), dict):
                    coordinates = str(loc_data['coordinates'])
                
                location = Location(
                    displayName=loc_data.get('displayName'),
                    address=loc_data.get('address', {}).get('street'),
                    coordinates=coordinates
                )

            organizer = None
            if event.get('organizer'):
                email_data = event['organizer'].get('emailAddress', {})
                organizer = Organizer(
                    emailAddress=EmailAddress(
                        name=email_data.get('name'),
                        address=email_data.get('address')
                    )
                )

            events.append(Event(
                id=event['id'],
                subject=event['subject'],
                body=event.get('body'),
                start=event['start'],
                end=event['end'],
                location=location,
                organizer=organizer,
                attendees=event.get('attendees'),
                web_link=event.get('webLink')
            ))
            
        return EventList(
            events=events,
            next_link=response.get('@odata.nextLink')
        )

    def get_event(self, event_id: str, calendar_id: Optional[str] = None) -> Event:
        event = self.client.get_event(event_id, calendar_id)
        
        location = None
        if event.get('location'):
            loc_data = event['location']
            location = Location(
                displayName=loc_data.get('displayName'),
                address=loc_data.get('address', {}).get('street', '') if loc_data.get('address') else None,
                coordinates=str(loc_data.get('coordinates')) if loc_data.get('coordinates') else None
            )

        organizer = None
        if event.get('organizer'):
            email_data = event['organizer'].get('emailAddress', {})
            organizer = Organizer(
                emailAddress=EmailAddress(
                    name=email_data.get('name'),
                    address=email_data.get('address', '')
                )
            )

        return Event(
            id=event['id'],
            subject=event['subject'],
            body=event.get('body'),
            start=event['start'],
            end=event['end'],
            location=location,
            organizer=organizer,
            attendees=event.get('attendees'),
            web_link=event.get('webLink', '')
        )

    def create_event(self, event: EventCreate, calendar_id: Optional[str] = None) -> Event:
        event_data = event.dict(exclude_none=True)
        response = self.client.create_event(event_data, calendar_id)
        return self.get_event(response['id'], calendar_id)

    def update_event(self, event_id: str, event: EventUpdate, 
                    calendar_id: Optional[str] = None) -> Event:
        event_data = event.dict(exclude_none=True)
        response = self.client.update_event(event_id, event_data, calendar_id)
        return self.get_event(response['id'], calendar_id)

    def delete_event(self, event_id: str, calendar_id: Optional[str] = None) -> None:
        self.client.delete_event(event_id, calendar_id)