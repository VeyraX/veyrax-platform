import { tool } from 'ai';
import { z } from 'zod';
import { dummyEvents } from '@/app/modules/agent/components/tools/eventbrite/event-card-dummydata';
import type { Event } from '@/app/modules/agent/components/tools/eventbrite/event-card-types';

export const getEventsTool = tool({
  description: 'Get a list of available events, optionally filtered by location',
  parameters: z.object({
    location: z.string().optional().describe('Optional location to filter events'),
  }),
  execute: async function({ location }): Promise<{ success: boolean, events?: Event[], error?: string }> {
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      let filteredEvents = dummyEvents;
      
      if (location) {
        filteredEvents = dummyEvents.filter(event => 
          !event.isOnline && 
          event.location.toLowerCase().includes(location.toLowerCase())
        );
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