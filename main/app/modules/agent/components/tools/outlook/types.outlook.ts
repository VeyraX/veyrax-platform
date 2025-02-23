// Basic Types
export interface EmailAddress {
    name?: string;
    address: string;
  }
  
  export interface Recipient {
    emailAddress: EmailAddress;
    type?: 'to' | 'cc' | 'bcc';
  }
  
  export interface Attachment {
    id: string;
    name: string;
    contentType: string;
    size: number;
    contentId?: string;
    isInline?: boolean;
  }
  
  // Message Types
  export interface MessageBody {
    contentType: 'text' | 'html';
    content: string;
  }
  
  export interface MessageProps {
    id: string;
    conversationId?: string;
    subject?: string;
    bodyPreview?: string;
    body?: string;
    from_address?: string;
    to?: string[];
    to_recipients?: string[];
    cc_recipients?: string[];
    bcc_recipients?: string[];
    sent_datetime?: string;
    received_datetime: string;
    hasAttachments?: boolean;
    attachments?: Attachment[];
    importance?: 'low' | 'normal' | 'high';
    isRead?: boolean;
    isDraft?: boolean;
    categories?: string[];
    webLink: string;
    flags?: {
      flagStatus?: 'notFlagged' | 'complete' | 'flagged';
      dueDateTime?: string;
    };
  }
  
  export interface DraftMessageProps {
    to: string;
    subject: string;
    body: string;
    cc?: string[];
    bcc?: string[];
    attachments?: {
      name: string;
      content: string;
      contentType: string;
    }[];
  }
  
  // Calendar Types
  export interface EventTime {
    dateTime: string;
    timeZone: string;
  }
  
  export interface Location {
    displayName?: string;
    address?: {
      street?: string;
      city?: string;
      state?: string;
      countryOrRegion?: string;
      postalCode?: string;
    };
    coordinates?: {
      latitude?: number;
      longitude?: number;
    };
    locationType?: 'default' | 'conferenceRoom' | 'homeAddress' | 'businessAddress' | 'online';
  }
  
  export interface Attendee {
    emailAddress: EmailAddress;
    type: 'required' | 'optional' | 'resource';
    status?: {
      response: 'none' | 'accepted' | 'tentativelyAccepted' | 'declined' | 'notResponded';
      time?: string;
    };
  }
  
  export interface Recurrence {
    pattern: {
      type: 'daily' | 'weekly' | 'monthly' | 'yearly';
      interval: number;
      daysOfWeek?: string[];
      dayOfMonth?: number;
      month?: number;
    };
    range: {
      type: 'endDate' | 'noEnd' | 'numbered';
      startDate: string;
      endDate?: string;
      numberOfOccurrences?: number;
    };
  }
  
  export interface EventProps {
    id: string;
    subject: string;
    body?: {
      contentType: 'text' | 'html';
      content: string;
    };
    start: EventTime;
    end: EventTime;
    location?: Location;
    locations?: Location[];
    isAllDay?: boolean;
    organizer: {
      emailAddress: EmailAddress;
    };
    attendees?: Attendee[];
    recurrence?: Recurrence;
    isOnlineMeeting?: boolean;
    onlineMeeting?: {
      joinUrl: string;
      conferenceId?: string;
      tollNumber?: string;
      providers?: string[];
    };
    importance?: 'low' | 'normal' | 'high';
    sensitivity?: 'normal' | 'personal' | 'private' | 'confidential';
    showAs?: 'free' | 'tentative' | 'busy' | 'oof' | 'workingElsewhere';
    categories?: string[];
    web_link: string;
  }
  
  export interface CalendarProps {
    id: string;
    name: string;
    color?: string;
    hexColor?: string;
    isDefaultCalendar?: boolean;
    canShare?: boolean;
    canViewPrivateItems?: boolean;
    owner?: {
      name?: string;
      address: string;
    };
  }
  
  // Response Types
  export interface MessageResponse {
    success: boolean;
    message?: MessageProps;
    error?: string;
  }
  
  export interface MessagesListResponse {
    success: boolean;
    messages?: MessageProps[];
    error?: string;
  }
  
  export interface EventResponse {
    success: boolean;
    event?: EventProps;
    error?: string;
  }
  
  export interface EventsListResponse {
    success: boolean;
    events?: EventProps[];
    error?: string;
  }
  
  export interface CalendarResponse {
    success: boolean;
    calendar?: CalendarProps;
    error?: string;
  }
  
  export interface CalendarsListResponse {
    success: boolean;
    calendars?: CalendarProps[];
    error?: string;
  }
  
  // Add this new interface for filters
  export interface Filters {
    search?: string;
    calendarId?: string;
    afterDate?: string;
    beforeDate?: string;
    maxResults?: number;
  }