import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';

export const googleCalendar_createEvent = tool({
  description: 'Create a new calendar event',
  parameters: z.object({
    summary: z.string().describe('Title of the event'),
    description: z.string().optional().describe('Description of the event'),
    location: z.string().optional().describe('Location of the event'),
    start: z.object({
      dateTime: z.string().describe('Start time in ISO format (e.g., 2024-03-20T10:00:00)'),
      timeZone: z.string().optional().describe('Timezone for start time')
    }),
    end: z.object({
      dateTime: z.string().describe('End time in ISO format (e.g., 2024-03-20T11:00:00)'),
      timeZone: z.string().optional().describe('Timezone for end time')
    }),
    attendees: z.array(z.object({
      email: z.string().describe('Attendee email address')
    })).optional().describe('List of event attendees')
  }),
  execute: async function({ summary, description, location, start, end, attendees }) {
    try {
      const headers = await getAuthHeaders();
      
      const response = await fetch('http://localhost:8000/google_calendar/events', {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({
          summary,
          description,
          location,
          start,
          end,
          attendees
        })
      });

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

export const googleCalendar_listEvents = tool({
  description: 'List calendar events with optional filters',
  parameters: z.object({
    keywords: z.string().optional().describe('Keywords to search in event title and description'),
    attendees: z.string().optional().describe('Filter by attendee email'),
    afterDate: z.string().optional().describe('Filter events after date (YYYY-MM-DD)'),
    beforeDate: z.string().optional().describe('Filter events before date (YYYY-MM-DD)'),
    calendarId: z.string().optional().describe('ID of the calendar to search (defaults to primary)')
  }),
  execute: async function({ keywords, attendees, afterDate, beforeDate, calendarId }) {
    try {
      const params = new URLSearchParams();
      if (keywords) params.append('keywords', keywords);
      if (attendees) params.append('attendees', attendees);
      if (afterDate) params.append('after_date', afterDate);
      if (beforeDate) params.append('before_date', beforeDate);
      if (calendarId) params.append('calendarId', calendarId);

      const headers = await getAuthHeaders();
      const response = await fetch(
        `http://localhost:8000/google_calendar/events?${params.toString()}`,
        {
          headers,
          credentials: 'include'
        }
      );
      if (!response.ok) throw new Error('Failed to fetch events');
      
      const data = await response.json();
      return {
        success: true,
        events: data.items,
        nextPageToken: data.nextPageToken
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch events'
      };
    }
  }
});
