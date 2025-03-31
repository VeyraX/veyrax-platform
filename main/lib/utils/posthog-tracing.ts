import { PostHog } from "posthog-node";
import { withTracing } from "@posthog/ai";
import crypto from 'crypto';

let phClient: PostHog | null = null;
try {
  phClient = new PostHog(
    process.env.NEXT_PUBLIC_POSTHOG_KEY || '',
    { host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com' }
  );
} catch (error) {
  console.error('Error initializing PostHog client:', error);
}

export function generateTraceId(): string {
  return crypto.randomUUID();
}

export function traceModel(model: any, userId: string, properties: {
  flow_id?: string;
  chat_id?: string;
  has_flow?: boolean;
  is_service_account?: boolean;
  user_email?: string;
  trace_id?: string;
  endpoint?: string;
  [key: string]: any;
}) {
  if (!phClient) {
    console.warn('PostHog client not initialized, returning model without tracing');
    return model;
  }

  const traceId = properties.trace_id || generateTraceId();

  try {
    return withTracing(
      model, 
      phClient, 
      {
        posthogDistinctId: userId,
        posthogTraceId: traceId,
        posthogProperties: { 
          trace_id: traceId,
          user_id: userId,
          ...properties
        }
      }
    );
  } catch (error) {
    console.error('Error applying PostHog tracing:', error);
    return model;
  }
}

export { phClient }; 