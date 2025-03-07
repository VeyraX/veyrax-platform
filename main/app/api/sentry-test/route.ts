import * as Sentry from "@sentry/nextjs";

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    // Intentionally throw an error
    throw new Error("Sentry API Error Test");
  } catch (error) {
    // Capture the error with Sentry
    Sentry.captureException(error);
    
    // Return error response
    return new Response(
      JSON.stringify({ message: "Error captured by Sentry on the server" }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
}

// This function demonstrates an unhandled server error
export async function POST() {
  // This error will be automatically captured by Sentry
  throw new Error("Sentry Unhandled API Error Test");
  
  // This line will never execute
  return Response.json({ message: 'This should not be returned' });
} 