import { tool } from 'ai';
import { z } from 'zod';
import { MessageProps, DraftMessageProps } from '@/app/modules/agent/components/tools/gmail/types.gmail';
import { createClient } from '@/lib/utils/supabase/server';
import { getAuthHeaders } from '@/lib/actions/actions';

export const gmail_createDraft = tool({
  description: 'Create a new draft email message',
  parameters: z.object({
    to: z.string().describe('Email address of the recipient'),
    subject: z.string().describe('Subject of the email'),
    body: z.string().describe('Body content of the email'),
  }),
  execute: async function({ to, subject, body }: DraftMessageProps): Promise<{ 
    success: boolean,
    draftId?: string,
    error?: string 
  }> {
    try {
      const headers = await getAuthHeaders();
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/gmail/drafts`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ to, subject, body }),
        credentials: 'include'
      });

      if (!response.ok) throw new Error('Failed to create draft');
      
      const data = await response.json();
      return {
        success: true,
        draftId: data.draft_id
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create draft'
      };
    }
  }
});

export const gmail_listMessages = tool({
  description: 'List email messages with optional filters',
  parameters: z.object({
    bodyKeywords: z.string().optional().describe('Keywords to search in email body'),
    recipient: z.string().optional().describe('Filter by recipient email'),
    subjectKeywords: z.string().optional().describe('Keywords to search in subject'),
    afterDate: z.string().optional().describe('Filter messages after date (YYYY-MM-DD)'),
    beforeDate: z.string().optional().describe('Filter messages before date (YYYY-MM-DD)'),
    maxResults: z.number().optional().describe('Maximum number of results to return (default: 20)'),
  }),
  execute: async function({ bodyKeywords, recipient, subjectKeywords, afterDate, beforeDate, maxResults }): Promise<{ 
    success: boolean,
    messages?: MessageProps[],
    error?: string 
  }> {
    try {
      const params = new URLSearchParams();
      if (bodyKeywords) params.append('body_keywords', bodyKeywords);
      if (recipient) params.append('recipient', recipient);
      if (subjectKeywords) params.append('subject_keywords', subjectKeywords);
      if (afterDate) params.append('after_date', afterDate);
      if (beforeDate) params.append('before_date', beforeDate);
      if (maxResults) params.append('max_results', maxResults.toString());

      const url = `${process.env.NEXT_PUBLIC_API_URL}/gmail/messages?${params.toString()}`;
      
      const headers = await getAuthHeaders();
      const response = await fetch(url, 
        { 
          method: 'GET',
          headers, 
          credentials: 'include' 
        });
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

export const gmail_sendMessage = tool({
  description: 'Send an existing draft message by its ID',
  parameters: z.object({
    messageId: z.string().describe('ID of the draft message to send'),
  }),
  execute: async function({ messageId }: { messageId: string }): Promise<{ 
    success: boolean,
    message?: MessageProps,
    error?: string 
  }> {
    try {
      const url = `${process.env.NEXT_PUBLIC_API_URL}/gmail/messages/${messageId}/send`;
      
      const headers = await getAuthHeaders();
      const response = await fetch(url, {
        method: 'POST',
        headers,
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }
      
      const message = await response.json();
      
      return {
        success: true,
        message
      };
    } catch (error) {
      console.error('Error sending message:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to send message'
      };
    }
  }
});
