import { tool } from 'ai';
import { z } from 'zod';
import { createPaymentIntent } from '@/app/modules/agent/components/tools/stripe/stripe-paymenet-intent';

export const createPaymentTool = tool({
  description: 'Create a payment intent for purchasing event tickets',
  parameters: z.object({
    eventId: z.string().describe('The ID of the event to purchase tickets for'),
    eventName: z.string().describe('The name of the event to purchase tickets for'),
    quantity: z.number().min(1).describe('Number of tickets to purchase'),
    pricePerTicket: z.number().min(0).describe('Price per ticket in USD'),
  }),
  execute: async function({ eventId, eventName, quantity, pricePerTicket }): Promise<{ success: boolean, clientSecret?: string, error?: string }> {
    try {
      const amount = Math.round(quantity * pricePerTicket * 100);
      
      const { clientSecret } = await createPaymentIntent(amount);
      
      return {
        success: true,
        clientSecret: clientSecret || undefined
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create payment'
      };
    }
  }
});