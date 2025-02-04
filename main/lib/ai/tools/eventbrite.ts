import { tool } from 'ai';
import { z } from 'zod';
import { dummyEvents } from '@/app/modules/agent/components/tools/eventbrite/event-card-dummydata';
import type { Event } from '@/app/modules/agent/components/tools/eventbrite/event-card-types';

export const getEventsTool = tool({
  description: 'Get a list of available events, filtered by location and/or date range',
  parameters: z.object({
    location: z.string().optional().describe('Location to filter events (e.g., "San Francisco")'),
    startDate: z.string().optional().describe('Start date for filtering events (YYYY-MM-DD)'),
    endDate: z.string().optional().describe('End date for filtering events (YYYY-MM-DD)'),
  }),
  execute: async function({ location, startDate, endDate }): Promise<{ success: boolean, events?: Event[], error?: string }> {
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      let filteredEvents = dummyEvents;
      
      if (location) {
        filteredEvents = filteredEvents.filter(event => 
          !event.isOnline && 
          event.location.toLowerCase().includes(location.toLowerCase())
        );
      }

      if (startDate || endDate) {
        filteredEvents = filteredEvents.filter(event => {
          const eventDate = new Date(event.startDate);
          const start = startDate ? new Date(startDate) : null;
          const end = endDate ? new Date(endDate) : null;

          if (start && end) {
            return eventDate >= start && eventDate <= end;
          } else if (start) {
            return eventDate >= start;
          } else if (end) {
            return eventDate <= end;
          }
          return true;
        });
      }

      return {
        success: true,
        events: filteredEvents
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch events'
      };
    }
  }
});

export const getEventDetailTool = tool({
  description: 'Get detailed information about a specific event by ID',
  parameters: z.object({
    eventId: z.string().describe('The ID of the event to fetch details for'),
  }),
  execute: async function({ eventId }): Promise<{ success: boolean, event?: Event, error?: string }> {
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const event = dummyEvents.find(e => e.id === eventId);
      
      if (!event) {
        return {
          success: false,
          error: 'Event not found'
        };
      }

      return {
        success: true,
        event
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch event details'
      };
    }
  }
});