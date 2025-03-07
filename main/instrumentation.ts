// instrumentation.ts
import { registerOTel } from "@vercel/otel";
import { LangfuseExporter } from "langfuse-vercel";
import { SentryPropagator } from "@sentry/opentelemetry";

export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./sentry.server.config");
  }

  if (process.env.NEXT_RUNTIME === "edge") {
    await import("./sentry.edge.config");
  }

  // Register OpenTelemetry with only the supported options
  registerOTel({
    serviceName: "veyrax-ai",
    traceExporter: new LangfuseExporter(),
    propagators: [new SentryPropagator()]
  });
}

// Capture errors from nested React Server Components
export { captureRequestError as onRequestError } from "@sentry/nextjs";