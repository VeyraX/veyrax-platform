# VeyraX — Agentic Component Interface

VeyraX is an infrastructure layer that connects AI agents to the tools people actually use.
One API key gives an agent (Claude, Cursor, your own LLM app) authenticated access to 80+ integrations
and thousands of MCP servers, plus long-term memory and multi-step automation flows.

## Features

- **Tool calling API** — a single, uniform interface (`/tools`, `/tool-call/{tool}/{method}`) over 80+
  integrations: Gmail, Google Calendar/Drive/Docs/Sheets, Slack, Notion, Linear, Jira, Confluence, GitHub,
  Outlook, Dropbox, Asana, Trello, Figma, Airtable, Vercel, Sentry, PostgreSQL, ClickHouse, Snowflake,
  Perplexity, Tavily, Exa, Firecrawl, Browserbase, E2B and many more (see `aci_server/integrations`).
- **OAuth & credential management** — users connect their accounts once; tokens and API keys are stored
  encrypted (AES) and injected into tool calls on their behalf.
- **MCP** — expose all connected tools to MCP clients, and deploy any GitHub-hosted MCP server
  "in two clicks" (Dockerfile generation, build via GitHub Actions, push to Docker Hub).
- **Memory** — retain information automatically across user requests and make it available to any agent.
- **Flows** — describe a routine in natural language, turn it into an agent-powered multi-step workflow,
  run it on demand or on a schedule.
- **Semantic tool search** — vector index over tools and providers so agents can find the right tool.
- **UI components** — integrations return structured components (`component.json`) that the frontend renders.

## Architecture

| Path | Description |
|------|-------------|
| `aci_server/` | Python backend: FastAPI app, integrations, agent runtime (OpenAI Agents SDK / OpenRouter), flows, memory, MCP deployment, Celery workers |
| `aci_server/integrations/<name>/` | One folder per integration: `client.py`, `service.py`, `route.py`, `schema.py`, `examples.yaml`, `component.json`, `tests.py` |
| `main/` | Next.js 14 web app: landing, dashboard, integrations, playground, flows, settings, billing (Stripe) |
| `services/whatsapp-bridge/` | Go service exposing WhatsApp through a REST API |
| `nginx/`, `docker-compose*.yml` | Deployment configuration (reverse proxy, Celery/Flower, Redis, Datadog) |
| `.github/workflows/` | GitHub Action that builds and publishes MCP server images |

Main dependencies: Supabase (Postgres + Auth + Storage), Redis, Upstash Vector / Qdrant, OpenAI or OpenRouter.

## Getting started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for the frontend)
- A Supabase project
- An OpenAI or OpenRouter API key

> Note: the Supabase database schema is not included in this repository yet.

### Configuration

1. Backend: `cp .env.example .env` and fill in the values you need.
2. Frontend: `cp main/.env.example main/.env.local` and fill in the values you need.
3. Never commit real `.env` files — they are git-ignored.

Only the integrations you configure credentials for will work; the rest can stay empty.

### Run the backend

```bash
docker-compose up --build
```

The API is available at `http://localhost:8000` (OpenAPI docs at `/docs`), Celery Flower at `http://localhost:5555`.

### Run the frontend

```bash
cd main
npm install
npm run dev
```

The web app is available at `http://localhost:3000`.

## Integration tests

1. Run all tests in Docker
```bash
docker-compose exec aci_server /app/run_tests.sh
```

2. Run tests for a specific integration
```bash
docker-compose exec aci_server /app/run_tests.sh dropbox
```

## Adding an integration

Create a new folder in `aci_server/integrations/` following the structure of an existing one
(for example `openweather`), and register its router in `aci_server/main.py`.
Conventions are described in `.cursor/rules/integration_rules.md`, `component_design.mdc` and `examples_rules.mdc`.

## License

[MIT](LICENSE)
