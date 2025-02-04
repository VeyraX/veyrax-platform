import { getEventsTool, getEventDetailTool } from './eventbrite';
import { createPaymentTool } from './stripe';

export const tools = {
  getEventsTool,
  getEventDetailTool,
  createPaymentTool,
};

export type Tools = typeof tools;
