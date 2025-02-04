import { getEventsTool, getEventDetailTool } from './eventbrite';
import { createPaymentTool } from './stripe';
import { generateComponentTool } from './generate-component';
import { createCalendarEventTool } from './calendar';

export const tools = {
  getEventsTool,
  getEventDetailTool,
  createPaymentTool,
  generateComponentTool,
  createCalendarEventTool,
};

export type Tools = typeof tools;
