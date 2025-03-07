'use client';

import * as Sentry from "@sentry/nextjs";
import { useState } from "react";

export default function SentryTestPage() {
  const [resultMessage, setResultMessage] = useState<string | null>(null);
  
  const triggerFrontendError = () => {
    try {
      // Intentionally throw an error
      throw new Error("Sentry Frontend Error Test");
    } catch (error) {
      // Capture and send to Sentry
      Sentry.captureException(error);
      setResultMessage("Frontend error triggered! Check your Sentry dashboard.");
    }
  };

  const triggerUnhandledError = () => {
    // This will be caught by Sentry's global error handler
    throw new Error("Sentry Unhandled Frontend Error Test");
  };

  const testApiError = async () => {
    try {
      const response = await fetch('/api/sentry-test');
      const data = await response.json();
      setResultMessage(data.message);
    } catch (error) {
      setResultMessage("API error triggered! Check your Sentry dashboard.");
    }
  };

  return (
    <div className="container mx-auto p-8 max-w-3xl">
      <h1 className="text-3xl font-bold mb-6">Sentry Test Page</h1>
      
      {resultMessage && (
        <div className="p-4 mb-6 bg-blue-100 border border-blue-300 rounded">
          <p>{resultMessage}</p>
        </div>
      )}
      
      <div className="space-y-8">
        <div className="p-6 border rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Handled Frontend Error</h2>
          <p className="mb-4">This will trigger a handled error that's captured with Sentry.captureException()</p>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={triggerFrontendError}
          >
            Trigger Handled Error
          </button>
        </div>

        <div className="p-6 border rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Unhandled Frontend Error</h2>
          <p className="mb-4">This will trigger an unhandled error that should be automatically captured by Sentry</p>
          <button
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            onClick={triggerUnhandledError}
          >
            Trigger Unhandled Error
          </button>
        </div>

        <div className="p-6 border rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-4">API Error Test</h2>
          <p className="mb-4">This will call an API endpoint that throws a server-side error</p>
          <button
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
            onClick={testApiError}
          >
            Trigger API Error
          </button>
        </div>
      </div>
    </div>
  );
} 