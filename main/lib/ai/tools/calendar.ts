import { tool } from 'ai';
import { z } from 'zod';
import { Event } from '@/app/modules/agent/components/tools/calendar/calendar-types';

export const createCalendarEventTool = tool({
  description: 'Create a new calendar event',
  parameters: z.object({
    name: z.string().describe('Name of the event'),
    date: z.string().describe('Date of the event (YYYY-MM-DD)'),
    time: z.string().describe('Time of the event (e.g., "10:00 AM")'),
  }),
  execute: async function({ name, date, time }): Promise<{ 
    success: boolean, 
    event?: Event,
    error?: string 
  }> {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newEvent: Event = {
        id: Date.now(),
        name,
        time,
        datetime: `${date}T00:00`,  
      };

      return {
        success: true,
        event: newEvent
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create calendar event'
      };
    }
  }
});