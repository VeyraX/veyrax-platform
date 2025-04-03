import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';

// Email tools
export const outlook_createDraft = tool({
  description: 'Create a new draft email message in Outlook',
  parameters: z.object({
    to: z.string().describe('Email address of the recipient'),
    subject: z.string().describe('Subject of the email'),
    body: z.string().describe('Body content of the email'),
  }),
  execute: async function({ to, subject, body }): Promise<{
    success: boolean,
    draftId?: string,
    error?: string
  }> {
    try {
      const headers = await getAuthHeaders();
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/outlook/messages/draft`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ 
          to_recipients: [to],
          subject,
          body 
        }),
        credentials: 'include'
      });

      if (!response.ok) throw new Error('Failed to create draft');
      
      const data = await response.json();
      return {
        success: true,
        draftId: data.id
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create draft'
      };
    }
  }
});

export const outlook_listMessages = tool({
  description: 'List Outlook email messages with optional filters',
  parameters: z.object({
    search: z.string().optional().describe('Search term for messages'),
    recipient: z.string().optional().describe('Filter by recipient email'),
    subject: z.string().optional().describe('Filter by subject keywords'),
    afterDate: z.string().optional().describe('Filter messages after date (YYYY-MM-DD)'),
    beforeDate: z.string().optional().describe('Filter messages before date (YYYY-MM-DD)'),
    maxResults: z.number().optional().describe('Maximum number of results to return'),
  }),
  execute: async function({ search, recipient, subject, afterDate, beforeDate, maxResults }) {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (recipient) params.append('to', recipient);
      if (subject) params.append('subject', subject);
      if (afterDate) params.append('after_date', afterDate);
      if (beforeDate) params.append('before_date', beforeDate);
      if (maxResults) params.append('max_results', maxResults.toString());

      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/outlook/messages?${params.toString()}`,
        { 
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) throw new Error('Failed to fetch messages');
      
      const data = await response.json();
      return {
        success: true,
        messages: data.messages
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch messages'
      };
    }
  }
});

export const outlook_sendMessage = tool({
  description: 'Send an existing Outlook draft message',
  parameters: z.object({
    messageId: z.string().describe('ID of the draft message to send'),
  }),
  execute: async function({ messageId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/outlook/messages/${messageId}/send`,
        {
          method: 'POST',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data = await response.json();
      return {
        success: true,
        message: data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to send message'
      };
    }
  }
});

// Calendar tools
export const outlook_listEvents = tool({
  description: 'List Outlook calendar events with optional filters',
  parameters: z.object({
    calendarId: z.string().optional().describe('Specific calendar ID to fetch events from'),
    search: z.string().optional().describe('Search term for events'),
    afterDate: z.string().optional().describe('Filter events after date (YYYY-MM-DD)'),
    beforeDate: z.string().optional().describe('Filter events before date (YYYY-MM-DD)'),
    maxResults: z.number().optional().describe('Maximum number of results to return'),
  }),
  execute: async function({ calendarId, search, afterDate, beforeDate, maxResults }) {
    try {
      const params = new URLSearchParams();
      if (calendarId) params.append('calendar_id', encodeURIComponent(calendarId));
      if (search) params.append('search', encodeURIComponent(search));
      if (afterDate) params.append('after_date', encodeURIComponent(afterDate));
      if (beforeDate) params.append('before_date', encodeURIComponent(beforeDate));
      if (maxResults) params.append('max_results', maxResults.toString());

      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/outlook/events?${params.toString()}`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) throw new Error('Failed to fetch events');

      const data = await response.json();
      return {
        success: true,
        events: data.events
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch events'
      };
    }
  }
});

export const outlook_createEvent = tool({
  description: 'Create a new event in Outlook calendar',
  parameters: z.object({
    subject: z.string().describe('Event subject/title'),
    start: z.object({
      dateTime: z.string().describe('Start date and time (ISO format)'),
      timeZone: z.string().describe('Time zone for start time')
    }),
    end: z.object({
      dateTime: z.string().describe('End date and time (ISO format)'),
      timeZone: z.string().describe('Time zone for end time')
    }),
    calendarId: z.string().optional().describe('Optional calendar ID to create event in'),
  }),
  execute: async function({ subject, start, end, calendarId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/outlook/events`,
        {
          method: 'POST',
          headers,
          body: JSON.stringify({
            subject,
            start,
            end,
            calendar_id: calendarId
          }),
          credentials: 'include'
        }
      );

      if (!response.ok) throw new Error('Failed to create event');

      const data = await response.json();
        return {
        success: true,
        event: data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create event'
      };
    }
  }
});

export const outlook_updateEvent = tool({
  description: 'Update an existing event in Outlook calendar',
  parameters: z.object({
    eventId: z.string().describe('ID of the event to update'),
    subject: z.string().optional().describe('Updated event subject/title'),
    start: z.object({
      dateTime: z.string().describe('Start date and time (ISO format)'),
      timeZone: z.string().describe('Time zone for start time')
    }).optional(),
    end: z.object({
      dateTime: z.string().describe('End date and time (ISO format)'),
      timeZone: z.string().describe('Time zone for end time')
    }).optional(),
    calendarId: z.string().optional().describe('Optional calendar ID containing the event'),
  }),
  execute: async function({ eventId, subject, start, end, calendarId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/outlook/events/${eventId}`,
        {
          method: 'PATCH',
          headers,
          body: JSON.stringify({
            subject,
            start,
            end,
            calendar_id: calendarId
          }),
          credentials: 'include'
        }
      );

      if (!response.ok) throw new Error('Failed to update event');

      const data = await response.json();
      return {
        success: true,
        event: data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update event'
      };
    }
  }
});

export const outlook_deleteEvent = tool({
  description: 'Delete an event from Outlook calendar',
  parameters: z.object({
    eventId: z.string().describe('ID of the event to delete'),
    calendarId: z.string().optional().describe('Optional calendar ID containing the event'),
  }),
  execute: async function({ eventId, calendarId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/outlook/events/${eventId}`,
        {
          method: 'DELETE',
          headers,
          body: JSON.stringify({ calendar_id: calendarId }),
          credentials: 'include'
        }
      );

      if (!response.ok) throw new Error('Failed to delete event');

      return {
        success: true,
        message: 'Event deleted successfully'
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete event'
      };
    }
  }
});