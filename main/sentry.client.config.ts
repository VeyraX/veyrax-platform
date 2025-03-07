import * as Sentry from "@sentry/nextjs";
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_URL || "",
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  
  // Performance Monitoring
  tracesSampleRate: 1.0,
  
  // Browser tracing and replay integrations
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({
      maskAllText: false,
      blockAllMedia: false,
    }),
  ],

  // Environment setting
  environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || "production"
});
