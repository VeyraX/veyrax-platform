<h1 align="center">VeyraX — Agentic Component Interface</h1>

<p align="center">
  <img src="docs/assets/banner.png" alt="VeyraX is Agentic Component Interface" width="800">
</p>

<p align="center">
  <b>One API key. 80+ tools. Any AI agent.</b><br>
  Open-source tool calling, OAuth, MCP, memory and flows for Claude, Cursor and your own LLM apps.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
  <a href="#integrations"><img src="https://img.shields.io/badge/integrations-83-brightgreen.svg" alt="83 integrations"></a>
  <img src="https://img.shields.io/badge/python-3.11-blue.svg" alt="Python 3.11">
  <img src="https://img.shields.io/badge/next.js-14-black.svg" alt="Next.js 14">
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs welcome"></a>
  <a href="https://x.com/vargastartup"><img src="https://img.shields.io/twitter/follow/vargastartup?style=flat&logo=x&label=Follow" alt="Follow @vargastartup on X"></a>
</p>

<p align="center">
  <a href="#quickstart">Quickstart</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#integrations">Integrations</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

VeyraX is an infrastructure layer that connects AI agents to the tools people actually use.
One API key gives an agent (Claude, Cursor, your own LLM app) authenticated access to 80+ integrations
and thousands of MCP servers, plus long-term memory and multi-step automation flows.

> [!TIP]
> If VeyraX is useful to you, give it a ⭐. It helps other people find the project.

## How it works

![Integrations → VeyraX → UI component](docs/assets/how-it-works.png)

The agent calls a tool through VeyraX; VeyraX authenticates on behalf of the user, calls the
underlying API and returns both structured data and a ready-to-render UI component.

<table>
  <tr>
    <td align="center"><img src="docs/assets/component-1.png" alt="Agent shows events as cards" width="260"></td>
    <td align="center"><img src="docs/assets/component-2.png" alt="Agent renders a checkout form" width="260"></td>
    <td align="center"><img src="docs/assets/component-3.png" alt="Agent adds an event to the calendar" width="260"></td>
  </tr>
</table>

## Features

- **Tool calling API** — a single, uniform interface (`/tools`, `/tool-call/{tool}/{method}`) over [80+](#integrations)
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

### Screenshots

| Integrations catalog | Connect a tool |
|---|---|
| ![Integrations catalog](docs/assets/tools.png) | ![Connect a tool](docs/assets/connect-tools.gif) |
| **Deploy an MCP server from GitHub** | **Create a flow from a prompt** |
| ![Deploy MCP](docs/assets/deploy-mcp.gif) | ![Create a flow](docs/assets/create-flow.gif) |
| **Memory** | **Flow overview & API** |
| ![Memory](docs/assets/memory.png) | ![Flow](docs/assets/flow.png) |
| **Auth for your users** | **Explore & deploy MCPs** |
| ![Auth](docs/assets/auth.png) | ![Deploy](docs/assets/deploy.png) |

## Architecture

| Path | Description |
|------|-------------|
| `aci_server/` | Python backend: FastAPI app, integrations, agent runtime (OpenAI Agents SDK / OpenRouter), flows, memory, MCP deployment, Celery workers |
| `aci_server/integrations/<name>/` | One folder per integration: `client.py`, `service.py`, `route.py`, `schema.py`, `examples.yaml`, `component.json`, `tests.py` |
| `main/` | Next.js 14 web app: landing, dashboard, integrations, playground, flows, settings, billing (Stripe) |
| `services/whatsapp-bridge/` | Go service exposing WhatsApp through a REST API |
| `nginx/`, `docker-compose*.yml` | Deployment configuration (reverse proxy, Celery/Flower, Redis, Datadog) |
| `.github/workflows/` | GitHub Action that builds and publishes MCP server images |

Main dependencies: Supabase (Postgres + Auth + Storage), Redis, Upstash Vector / Qdrant, OpenRouter (all LLM, embedding and
speech-to-text calls; models are set in `aci_server/llm.py` and `main/lib/ai/openrouter.ts`).

## Integrations

83 integrations live in [`aci_server/integrations`](aci_server/integrations); 79 of them are registered by default
and loaded into the tool catalog. Each one is exposed as `/{integration}/{method}` and through the unified
`/tool-call/{tool}/{method}` endpoint.

Auth: **OAuth** — user connects an account; **API key** — user's or server key; **RapidAPI** — key from
[RapidAPI](https://rapidapi.com); **Credentials** — host/user/password or connection string; **None** — public API.

Integrations marked with † are implemented but not registered in `INTEGRATION_ROUTERS` (`aci_server/main.py`).

| Category | Integrations |
|---|---|
| **Productivity & Docs** | <a href="aci_server/integrations/airtable"><img src="main/public/provider-logos/airtable.svg" alt="Airtable" title="Airtable" width="32" height="32"></a> <a href="aci_server/integrations/asana"><img src="main/public/provider-logos/asana.svg" alt="Asana" title="Asana" width="32" height="32"></a> <a href="aci_server/integrations/cal"><img src="main/public/provider-logos/cal.svg" alt="Cal.com" title="Cal.com" width="32" height="32"></a> <a href="aci_server/integrations/coda"><img src="main/public/provider-logos/coda.svg" alt="Coda" title="Coda" width="32" height="32"></a> <a href="aci_server/integrations/confluence"><img src="main/public/provider-logos/confluence.svg" alt="Confluence" title="Confluence" width="32" height="32"></a> <a href="aci_server/integrations/dropbox"><img src="main/public/provider-logos/dropbox.svg" alt="Dropbox" title="Dropbox" width="32" height="32"></a> <a href="aci_server/integrations/figma"><img src="main/public/provider-logos/figma.svg" alt="Figma" title="Figma" width="32" height="32"></a> <a href="aci_server/integrations/google_calendar"><img src="main/public/provider-logos/google-calendar.svg" alt="Google Calendar" title="Google Calendar" width="32" height="32"></a> <a href="aci_server/integrations/google_docs"><img src="main/public/provider-logos/google-docs.svg" alt="Google Docs" title="Google Docs" width="32" height="32"></a> <a href="aci_server/integrations/google_drive"><img src="main/public/provider-logos/google-drive.svg" alt="Google Drive" title="Google Drive" width="32" height="32"></a> <a href="aci_server/integrations/google_sheets"><img src="main/public/provider-logos/google-sheets.svg" alt="Google Sheets" title="Google Sheets" width="32" height="32"></a> <a href="aci_server/integrations/motion"><img src="main/public/provider-logos/motion.svg" alt="Motion" title="Motion" width="32" height="32"></a> <a href="aci_server/integrations/notion"><img src="main/public/provider-logos/notion.svg" alt="Notion" title="Notion" width="32" height="32"></a> <a href="aci_server/integrations/readwise"><img src="main/public/provider-logos/readwise.png" alt="Readwise" title="Readwise" width="32" height="32"></a> <a href="aci_server/integrations/ticktick"><img src="main/public/provider-logos/ticktick.jpeg" alt="TickTick" title="TickTick" width="32" height="32"></a> <a href="aci_server/integrations/todoist"><img src="main/public/provider-logos/todoist.svg" alt="Todoist" title="Todoist" width="32" height="32"></a> <a href="aci_server/integrations/trello"><img src="main/public/provider-logos/trello.svg" alt="Trello" title="Trello" width="32" height="32"></a> <a href="aci_server/integrations/typeform"><img src="main/public/provider-logos/typeform.svg" alt="Typeform" title="Typeform" width="32" height="32"></a> |
| **Communication** | <a href="aci_server/integrations/mail"><img src="main/public/provider-logos/mail.svg" alt="Mail (IMAP/SMTP)" title="Mail (IMAP/SMTP)" width="32" height="32"></a> <a href="aci_server/integrations/outlook"><img src="main/public/provider-logos/outlook.svg" alt="Outlook" title="Outlook" width="32" height="32"></a> <a href="aci_server/integrations/resend"><img src="main/public/provider-logos/resend.svg" alt="Resend" title="Resend" width="32" height="32"></a> <a href="aci_server/integrations/slack"><img src="main/public/provider-logos/slack.svg" alt="Slack" title="Slack" width="32" height="32"></a> <a href="aci_server/integrations/whatsapp"><img src="main/public/provider-logos/whatsapp.png" alt="WhatsApp" title="WhatsApp" width="32" height="32"></a> |
| **Developer tools & Infrastructure** | <a href="aci_server/integrations/twentyfirst_dev"><img src="main/public/provider-logos/twentyfirst_dev.png" alt="21st.dev" title="21st.dev" width="32" height="32"></a> <a href="aci_server/integrations/browser_use"><img src="main/public/provider-logos/browser-use.svg" alt="Browser Use" title="Browser Use" width="32" height="32"></a> <a href="aci_server/integrations/browserbase"><img src="main/public/provider-logos/browserbase.svg" alt="Browserbase" title="Browserbase" width="32" height="32"></a> <a href="aci_server/integrations/e2b"><img src="main/public/provider-logos/e2b.svg" alt="E2B" title="E2B" width="32" height="32"></a> <a href="aci_server/integrations/github"><img src="main/public/provider-logos/github.svg" alt="GitHub" title="GitHub" width="32" height="32"></a> <a href="aci_server/integrations/jira"><img src="main/public/provider-logos/jira.svg" alt="Jira" title="Jira" width="32" height="32"></a> <a href="aci_server/integrations/linear"><img src="main/public/provider-logos/linear.svg" alt="Linear" title="Linear" width="32" height="32"></a> <a href="aci_server/integrations/n8n"><img src="main/public/provider-logos/n8n.svg" alt="n8n" title="n8n" width="32" height="32"></a> <a href="aci_server/integrations/posthog"><img src="main/public/provider-logos/posthog.svg" alt="PostHog" title="PostHog" width="32" height="32"></a> <a href="aci_server/integrations/postman"><img src="main/public/provider-logos/postman.svg" alt="Postman" title="Postman" width="32" height="32"></a> <a href="aci_server/integrations/sentry"><img src="main/public/provider-logos/sentry.jpeg" alt="Sentry" title="Sentry" width="32" height="32"></a> <a href="aci_server/integrations/uploadthing"><img src="main/public/provider-logos/uploadthing.png" alt="UploadThing" title="UploadThing" width="32" height="32"></a> <a href="aci_server/integrations/vercel"><img src="main/public/provider-logos/vercel.svg" alt="Vercel" title="Vercel" width="32" height="32"></a> |
| **Databases** | <a href="aci_server/integrations/clickhouse"><img src="main/public/provider-logos/clickhouse.svg" alt="ClickHouse" title="ClickHouse" width="32" height="32"></a> <a href="aci_server/integrations/neondb"><img src="main/public/provider-logos/neondb.svg" alt="Neon" title="Neon" width="32" height="32"></a> <a href="aci_server/integrations/postgresql"><img src="main/public/provider-logos/postgresql.svg" alt="PostgreSQL" title="PostgreSQL" width="32" height="32"></a> <a href="aci_server/integrations/snowflake"><img src="main/public/provider-logos/snowflake.svg" alt="Snowflake" title="Snowflake" width="32" height="32"></a> <a href="aci_server/integrations/supabase"><img src="main/public/provider-logos/supabase.svg" alt="Supabase" title="Supabase" width="32" height="32"></a> |
| **Search & Web** | <a href="aci_server/integrations/brave"><img src="main/public/provider-logos/brave.svg" alt="Brave Search" title="Brave Search" width="32" height="32"></a> <a href="aci_server/integrations/duckduckgo"><img src="main/public/provider-logos/duckduckgo.svg" alt="DuckDuckGo" title="DuckDuckGo" width="32" height="32"></a> <a href="aci_server/integrations/exa"><img src="main/public/provider-logos/exa.png" alt="Exa" title="Exa" width="32" height="32"></a> <a href="aci_server/integrations/firecrawl"><img src="main/public/provider-logos/firecrawl.svg" alt="Firecrawl" title="Firecrawl" width="32" height="32"></a> <a href="aci_server/integrations/hacker_news"><img src="main/public/provider-logos/hacker-news.svg" alt="Hacker News" title="Hacker News" width="32" height="32"></a> <a href="aci_server/integrations/tavily"><img src="main/public/provider-logos/tavily.webp" alt="Tavily" title="Tavily" width="32" height="32"></a> <a href="aci_server/integrations/youtube"><img src="main/public/provider-logos/youtube.svg" alt="YouTube" title="YouTube" width="32" height="32"></a> |
| **AI & Media** | <a href="aci_server/integrations/bannerbear"><img src="main/public/provider-logos/bannerbear.png" alt="Bannerbear" title="Bannerbear" width="32" height="32"></a> <a href="aci_server/integrations/cloudinary"><img src="main/public/provider-logos/cloudinary.png" alt="Cloudinary" title="Cloudinary" width="32" height="32"></a> <a href="aci_server/integrations/falai"><img src="main/public/provider-logos/falai.svg" alt="fal.ai" title="fal.ai" width="32" height="32"></a> <a href="aci_server/integrations/heygen"><img src="main/public/provider-logos/heygen.svg" alt="HeyGen" title="HeyGen" width="32" height="32"></a> <a href="aci_server/integrations/perplexity"><img src="main/public/provider-logos/perplexity.svg" alt="Perplexity" title="Perplexity" width="32" height="32"></a> <a href="aci_server/integrations/replicate"><img src="main/public/provider-logos/replicate.png" alt="Replicate" title="Replicate" width="32" height="32"></a> <a href="aci_server/integrations/revid"><img src="main/public/provider-logos/revid.png" alt="Revid" title="Revid" width="32" height="32"></a> |
| **CRM & Sales** | <a href="aci_server/integrations/apollo"><img src="main/public/provider-logos/apollo.svg" alt="Apollo" title="Apollo" width="32" height="32"></a> <a href="aci_server/integrations/hunterio"><img src="main/public/provider-logos/hunterio.png" alt="Hunter.io" title="Hunter.io" width="32" height="32"></a> |
| **Social** | <a href="aci_server/integrations/facebook"><img src="main/public/provider-logos/facebook.svg" alt="Facebook" title="Facebook" width="32" height="32"></a> <a href="aci_server/integrations/instagram"><img src="main/public/provider-logos/instagram.svg" alt="Instagram" title="Instagram" width="32" height="32"></a> <a href="aci_server/integrations/linkedin"><img src="main/public/provider-logos/linkedin.svg" alt="LinkedIn" title="LinkedIn" width="32" height="32"></a> <a href="aci_server/integrations/reddit"><img src="main/public/provider-logos/reddit.svg" alt="Reddit" title="Reddit" width="32" height="32"></a> <a href="aci_server/integrations/x"><img src="main/public/provider-logos/x.svg" alt="X (Twitter)" title="X (Twitter)" width="32" height="32"></a> |
| **Travel, Local & Real Estate** | <a href="aci_server/integrations/airbnb"><img src="main/public/provider-logos/airbnb.svg" alt="Airbnb" title="Airbnb" width="32" height="32"></a> <a href="aci_server/integrations/google_maps"><img src="main/public/provider-logos/google-maps.svg" alt="Google Maps" title="Google Maps" width="32" height="32"></a> <a href="aci_server/integrations/skyscanner"><img src="main/public/provider-logos/skyscanner.svg" alt="Skyscanner" title="Skyscanner" width="32" height="32"></a> <a href="aci_server/integrations/yelp"><img src="main/public/provider-logos/yelp.svg" alt="Yelp" title="Yelp" width="32" height="32"></a> <a href="aci_server/integrations/zillow"><img src="main/public/provider-logos/zillow.svg" alt="Zillow" title="Zillow" width="32" height="32"></a> |
| **Commerce & Finance** | <a href="aci_server/integrations/amazon"><img src="main/public/provider-logos/amazon.png" alt="Amazon" title="Amazon" width="32" height="32"></a> <a href="aci_server/integrations/binance_p2p"><img src="main/public/provider-logos/binance_p2p.png" alt="Binance P2P" title="Binance P2P" width="32" height="32"></a> <a href="aci_server/integrations/bybit_p2p"><img src="main/public/provider-logos/bybit_p2p.jpg" alt="Bybit P2P" title="Bybit P2P" width="32" height="32"></a> <a href="aci_server/integrations/okx_p2p"><img src="main/public/provider-logos/okx_p2p.png" alt="OKX P2P" title="OKX P2P" width="32" height="32"></a> |
| **Utilities** | <a href="aci_server/integrations/dub"><img src="main/public/provider-logos/dub.svg" alt="Dub" title="Dub" width="32" height="32"></a> <a href="aci_server/integrations/http_request"><img src="main/public/provider-logos/http-request.svg" alt="HTTP Request" title="HTTP Request" width="32" height="32"></a> <a href="aci_server/integrations/ipinfo"><img src="main/public/provider-logos/ipinfo.svg" alt="IPinfo" title="IPinfo" width="32" height="32"></a> <a href="aci_server/integrations/openweather"><img src="main/public/provider-logos/openweather.png" alt="OpenWeather" title="OpenWeather" width="32" height="32"></a> <a href="aci_server/integrations/svgl"><img src="main/public/provider-logos/svgl.svg" alt="SVGL" title="SVGL" width="32" height="32"></a> <a href="aci_server/integrations/zip_code"><img src="main/public/provider-logos/zip_code.png" alt="Zip Code" title="Zip Code" width="32" height="32"></a> |
| **VeyraX** | <a href="aci_server/integrations/veyrax"><img src="main/public/provider-logos/veyrax.svg" alt="VeyraX Memory" title="VeyraX Memory" width="32" height="32"></a> <a href="aci_server/integrations/veyrax_auth"><img src="main/public/provider-logos/veyrax-auth.svg" alt="VeyraX Auth" title="VeyraX Auth" width="32" height="32"></a> |

Click a category below for what an agent can do with each integration.

<details>
<summary><b>Productivity & Docs</b> (19)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/airtable.svg" width="20" height="20" align="top"> [Airtable](aci_server/integrations/airtable) | Records CRUD, attachments, CSV sync, fields and tables | OAuth |
| <img src="main/public/provider-logos/asana.svg" width="20" height="20" align="top"> [Asana](aci_server/integrations/asana) | Tasks, subtasks, projects, tags, teams, workspaces | OAuth |
| <img src="main/public/provider-logos/cal.svg" width="20" height="20" align="top"> [Cal.com](aci_server/integrations/cal) | Bookings (create, reschedule, cancel), schedules, event types | API key |
| <img src="main/public/provider-logos/coda.svg" width="20" height="20" align="top"> [Coda](aci_server/integrations/coda) | Docs, pages, tables, columns and rows, page export | API key |
| <img src="main/public/provider-logos/confluence.svg" width="20" height="20" align="top"> [Confluence](aci_server/integrations/confluence) | Spaces, pages CRUD, content search | OAuth |
| <img src="main/public/provider-logos/docusign.svg" width="20" height="20" align="top"> [DocuSign](aci_server/integrations/docusign) † | Envelopes, documents, signing views | OAuth |
| <img src="main/public/provider-logos/dropbox.svg" width="20" height="20" align="top"> [Dropbox](aci_server/integrations/dropbox) | Files and folders: list, upload, download, move, share, search | OAuth |
| <img src="main/public/provider-logos/figma.svg" width="20" height="20" align="top"> [Figma](aci_server/integrations/figma) | Files, nodes, images, components, styles, team projects | OAuth |
| <img src="main/public/provider-logos/google-calendar.svg" width="20" height="20" align="top"> [Google Calendar](aci_server/integrations/google_calendar) | Calendars and events CRUD | OAuth |
| <img src="main/public/provider-logos/google-docs.svg" width="20" height="20" align="top"> [Google Docs](aci_server/integrations/google_docs) | Create, read, edit and search documents | OAuth |
| <img src="main/public/provider-logos/google-drive.svg" width="20" height="20" align="top"> [Google Drive](aci_server/integrations/google_drive) | Files and folders, upload/download, permissions | OAuth |
| <img src="main/public/provider-logos/google-sheets.svg" width="20" height="20" align="top"> [Google Sheets](aci_server/integrations/google_sheets) | Read/write/append values, sheets, formulas, search | OAuth |
| <img src="main/public/provider-logos/motion.svg" width="20" height="20" align="top"> [Motion](aci_server/integrations/motion) | Tasks, recurring tasks, projects, comments, schedules | API key |
| <img src="main/public/provider-logos/notion.svg" width="20" height="20" align="top"> [Notion](aci_server/integrations/notion) | Databases, pages, blocks, search, users | OAuth |
| <img src="main/public/provider-logos/readwise.png" width="20" height="20" align="top"> [Readwise](aci_server/integrations/readwise) | Save, list, update and delete Reader documents | API key |
| <img src="main/public/provider-logos/ticktick.jpeg" width="20" height="20" align="top"> [TickTick](aci_server/integrations/ticktick) | Tasks and projects | OAuth |
| <img src="main/public/provider-logos/todoist.svg" width="20" height="20" align="top"> [Todoist](aci_server/integrations/todoist) | Projects, sections, tasks, labels, comments | OAuth |
| <img src="main/public/provider-logos/trello.svg" width="20" height="20" align="top"> [Trello](aci_server/integrations/trello) | Boards, lists, cards, checklists, organizations | OAuth |
| <img src="main/public/provider-logos/typeform.svg" width="20" height="20" align="top"> [Typeform](aci_server/integrations/typeform) | Forms, responses, webhooks, workspaces | API key |

</details>
<details>
<summary><b>Communication</b> (6)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/gmail.svg" width="20" height="20" align="top"> [Gmail](aci_server/integrations/gmail) † | Read, send and delete messages, drafts | OAuth |
| <img src="main/public/provider-logos/mail.svg" width="20" height="20" align="top"> [Mail (IMAP/SMTP)](aci_server/integrations/mail) | Any mailbox: read, send, folders, auto-detect server settings | Credentials |
| <img src="main/public/provider-logos/outlook.svg" width="20" height="20" align="top"> [Outlook](aci_server/integrations/outlook) | Messages, drafts, calendars and events | OAuth |
| <img src="main/public/provider-logos/resend.svg" width="20" height="20" align="top"> [Resend](aci_server/integrations/resend) | Send emails (single/batch), broadcasts, domains, audiences, contacts | API key |
| <img src="main/public/provider-logos/slack.svg" width="20" height="20" align="top"> [Slack](aci_server/integrations/slack) | Channels, messages, DMs, threads | OAuth |
| <img src="main/public/provider-logos/whatsapp.png" width="20" height="20" align="top"> [WhatsApp](aci_server/integrations/whatsapp) | Chats, messages, contacts via the [WhatsApp bridge](services/whatsapp-bridge) | QR pairing |

</details>
<details>
<summary><b>Developer tools & Infrastructure</b> (13)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/twentyfirst_dev.png" width="20" height="20" align="top"> [21st.dev](aci_server/integrations/twentyfirst_dev) | Search UI components, generate component prompts | API key |
| <img src="main/public/provider-logos/browser-use.svg" width="20" height="20" align="top"> [Browser Use](aci_server/integrations/browser_use) | Run and control browser automation tasks | API key |
| <img src="main/public/provider-logos/browserbase.svg" width="20" height="20" align="top"> [Browserbase](aci_server/integrations/browserbase) | Headless browser sessions, contexts, logs, recordings | API key |
| <img src="main/public/provider-logos/e2b.svg" width="20" height="20" align="top"> [E2B](aci_server/integrations/e2b) | Code sandboxes: run code and commands, files | API key |
| <img src="main/public/provider-logos/github.svg" width="20" height="20" align="top"> [GitHub](aci_server/integrations/github) | Repositories, issues, pull requests, commits, reviews | OAuth |
| <img src="main/public/provider-logos/jira.svg" width="20" height="20" align="top"> [Jira](aci_server/integrations/jira) | Issues CRUD, projects, statuses, transitions, users | OAuth |
| <img src="main/public/provider-logos/linear.svg" width="20" height="20" align="top"> [Linear](aci_server/integrations/linear) | Issues (search, create, update, comment), projects, teams | OAuth |
| <img src="main/public/provider-logos/n8n.svg" width="20" height="20" align="top"> [n8n](aci_server/integrations/n8n) | Workflows, executions, users, credentials, tags | API key |
| <img src="main/public/provider-logos/posthog.svg" width="20" height="20" align="top"> [PostHog](aci_server/integrations/posthog) | HogQL queries, insights, dashboards, events, projects | API key |
| <img src="main/public/provider-logos/postman.svg" width="20" height="20" align="top"> [Postman](aci_server/integrations/postman) | Collections, environments, workspaces | API key |
| <img src="main/public/provider-logos/sentry.jpeg" width="20" height="20" align="top"> [Sentry](aci_server/integrations/sentry) | Teams, projects, issues, releases, alert rules | OAuth |
| <img src="main/public/provider-logos/uploadthing.png" width="20" height="20" align="top"> [UploadThing](aci_server/integrations/uploadthing) | File uploads (incl. from URL), file management | API key |
| <img src="main/public/provider-logos/vercel.svg" width="20" height="20" align="top"> [Vercel](aci_server/integrations/vercel) | Projects, deployments, domains, environment variables | OAuth |

</details>
<details>
<summary><b>Databases</b> (5)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/clickhouse.svg" width="20" height="20" align="top"> [ClickHouse](aci_server/integrations/clickhouse) | Run queries, list tables and columns | Credentials |
| <img src="main/public/provider-logos/neondb.svg" width="20" height="20" align="top"> [Neon](aci_server/integrations/neondb) | Run queries, list tables and columns | Credentials |
| <img src="main/public/provider-logos/postgresql.svg" width="20" height="20" align="top"> [PostgreSQL](aci_server/integrations/postgresql) | Run queries, list tables and columns | Credentials |
| <img src="main/public/provider-logos/snowflake.svg" width="20" height="20" align="top"> [Snowflake](aci_server/integrations/snowflake) | Run queries, list tables and columns | Credentials |
| <img src="main/public/provider-logos/supabase.svg" width="20" height="20" align="top"> [Supabase](aci_server/integrations/supabase) | Run queries, list tables and columns | Credentials |

</details>
<details>
<summary><b>Search & Web</b> (7)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/brave.svg" width="20" height="20" align="top"> [Brave Search](aci_server/integrations/brave) | Web, image, video and news search | API key |
| <img src="main/public/provider-logos/duckduckgo.svg" width="20" height="20" align="top"> [DuckDuckGo](aci_server/integrations/duckduckgo) | Search and fetch page content | None |
| <img src="main/public/provider-logos/exa.png" width="20" height="20" align="top"> [Exa](aci_server/integrations/exa) | Neural search, page contents, similar pages | API key |
| <img src="main/public/provider-logos/firecrawl.svg" width="20" height="20" align="top"> [Firecrawl](aci_server/integrations/firecrawl) | Scrape, crawl, map sites, structured extraction | API key |
| <img src="main/public/provider-logos/hacker-news.svg" width="20" height="20" align="top"> [Hacker News](aci_server/integrations/hacker_news) | Top/new/best stories, items, comments, users | None |
| <img src="main/public/provider-logos/tavily.webp" width="20" height="20" align="top"> [Tavily](aci_server/integrations/tavily) | Web search and content extraction | API key |
| <img src="main/public/provider-logos/youtube.svg" width="20" height="20" align="top"> [YouTube](aci_server/integrations/youtube) | Search videos, video details, captions, transcripts | API key |

</details>
<details>
<summary><b>AI & Media</b> (7)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/bannerbear.png" width="20" height="20" align="top"> [Bannerbear](aci_server/integrations/bannerbear) | Generate images, videos, GIFs and collections from templates | API key |
| <img src="main/public/provider-logos/cloudinary.png" width="20" height="20" align="top"> [Cloudinary](aci_server/integrations/cloudinary) | Upload, transform, rename and delete assets | API key |
| <img src="main/public/provider-logos/falai.svg" width="20" height="20" align="top"> [fal.ai](aci_server/integrations/falai) | Discover and run generative models, queue status, uploads | API key |
| <img src="main/public/provider-logos/heygen.svg" width="20" height="20" align="top"> [HeyGen](aci_server/integrations/heygen) | Avatar videos, voices, templates, translation | API key |
| <img src="main/public/provider-logos/perplexity.svg" width="20" height="20" align="top"> [Perplexity](aci_server/integrations/perplexity) | Web-grounded chat completions | API key |
| <img src="main/public/provider-logos/replicate.png" width="20" height="20" align="top"> [Replicate](aci_server/integrations/replicate) | Run models, predictions, deployments, trainings | API key |
| <img src="main/public/provider-logos/revid.png" width="20" height="20" align="top"> [Revid](aci_server/integrations/revid) | Generate and publish short-form videos | API key |

</details>
<details>
<summary><b>CRM & Sales</b> (3)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/apollo.svg" width="20" height="20" align="top"> [Apollo](aci_server/integrations/apollo) | Search people and organizations, get details | RapidAPI |
| <img src="main/public/provider-logos/hilvl.png" width="20" height="20" align="top"> [HighLevel](aci_server/integrations/hilvl) † | Businesses, calendars, slots, contacts and more | API key |
| <img src="main/public/provider-logos/hunterio.png" width="20" height="20" align="top"> [Hunter.io](aci_server/integrations/hunterio) | Domain search, email finder/verifier, enrichment | API key |

</details>
<details>
<summary><b>Social</b> (5)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/facebook.svg" width="20" height="20" align="top"> [Facebook](aci_server/integrations/facebook) | Search and read public pages, posts, groups, events | RapidAPI |
| <img src="main/public/provider-logos/instagram.svg" width="20" height="20" align="top"> [Instagram](aci_server/integrations/instagram) | Profiles, posts, comments, followers | RapidAPI |
| <img src="main/public/provider-logos/linkedin.svg" width="20" height="20" align="top"> [LinkedIn](aci_server/integrations/linkedin) | Profiles, companies, posts, jobs, people search | RapidAPI |
| <img src="main/public/provider-logos/reddit.svg" width="20" height="20" align="top"> [Reddit](aci_server/integrations/reddit) | Read, post, comment, edit, vote, search | OAuth |
| <img src="main/public/provider-logos/x.svg" width="20" height="20" align="top"> [X (Twitter)](aci_server/integrations/x) | Profiles, timelines, tweets, threads, lists, search | RapidAPI |

</details>
<details>
<summary><b>Travel, Local & Real Estate</b> (5)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/airbnb.svg" width="20" height="20" align="top"> [Airbnb](aci_server/integrations/airbnb) | Search listings, listing details | None |
| <img src="main/public/provider-logos/google-maps.svg" width="20" height="20" align="top"> [Google Maps](aci_server/integrations/google_maps) | Geocoding, places, directions, distance matrix, elevation | API key |
| <img src="main/public/provider-logos/skyscanner.svg" width="20" height="20" align="top"> [Skyscanner](aci_server/integrations/skyscanner) | Flights (one-way, round-trip, anywhere), price calendars, hotels | RapidAPI |
| <img src="main/public/provider-logos/yelp.svg" width="20" height="20" align="top"> [Yelp](aci_server/integrations/yelp) | Search businesses, details, reviews, menus | RapidAPI |
| <img src="main/public/provider-logos/zillow.svg" width="20" height="20" align="top"> [Zillow](aci_server/integrations/zillow) | Properties, Zestimates, comps, market data | RapidAPI |

</details>
<details>
<summary><b>Commerce & Finance</b> (4)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/amazon.png" width="20" height="20" align="top"> [Amazon](aci_server/integrations/amazon) | Product search, items, variations, browse nodes (PA-API) | API key |
| <img src="main/public/provider-logos/binance_p2p.png" width="20" height="20" align="top"> [Binance P2P](aci_server/integrations/binance_p2p) | P2P crypto offers | RapidAPI |
| <img src="main/public/provider-logos/bybit_p2p.jpg" width="20" height="20" align="top"> [Bybit P2P](aci_server/integrations/bybit_p2p) | P2P crypto offers | RapidAPI |
| <img src="main/public/provider-logos/okx_p2p.png" width="20" height="20" align="top"> [OKX P2P](aci_server/integrations/okx_p2p) | P2P crypto offers | RapidAPI |

</details>
<details>
<summary><b>Utilities</b> (6)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/dub.svg" width="20" height="20" align="top"> [Dub](aci_server/integrations/dub) | Short links (bulk too), QR codes, analytics, events | API key |
| <img src="main/public/provider-logos/http-request.svg" width="20" height="20" align="top"> [HTTP Request](aci_server/integrations/http_request) | Call any HTTP endpoint | None |
| <img src="main/public/provider-logos/ipinfo.svg" width="20" height="20" align="top"> [IPinfo](aci_server/integrations/ipinfo) | IP geolocation (single/bulk), ASN info | API key |
| <img src="main/public/provider-logos/openweather.png" width="20" height="20" align="top"> [OpenWeather](aci_server/integrations/openweather) | Weather forecast | API key |
| <img src="main/public/provider-logos/svgl.svg" width="20" height="20" align="top"> [SVGL](aci_server/integrations/svgl) | Search SVG brand logos by name or category | None |
| <img src="main/public/provider-logos/zip_code.png" width="20" height="20" align="top"> [Zip Code](aci_server/integrations/zip_code) | Look up places by zip code or city | None |

</details>
<details>
<summary><b>VeyraX</b> (3)</summary>

| Integration | What an agent can do | Auth |
|---|---|---|
| <img src="main/public/provider-logos/veyrax.svg" width="20" height="20" align="top"> [VeyraX Memory](aci_server/integrations/veyrax) | Save, get, update and delete user memories | VeyraX API key |
| <img src="main/public/provider-logos/veyrax-auth.svg" width="20" height="20" align="top"> [VeyraX Auth](aci_server/integrations/veyrax_auth) | Tool connection status, connection links | VeyraX API key |
| <img src="main/public/provider-logos/veyrax-mcp.svg" width="20" height="20" align="top"> [VeyraX MCP](aci_server/integrations/veyrax-mcp) † | Search and deploy MCP servers, connection links | VeyraX API key |

</details>

## Quickstart

You need [Docker](https://docs.docker.com/get-docker/) (running), the
[Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started) and Node.js 18+. Then, from the
repository root:

```bash
./quickstart.sh
```

One command, safe to re-run. It:

1. starts a local Supabase with the full schema and the tool catalog (79 integrations, ~930 actions);
2. creates `.env` and `main/.env.local` for it (existing files are kept);
3. starts the backend with Docker Compose and the frontend with Next.js;
4. runs a smoke test: creates a demo user and an API key, connects Hacker News and calls a tool through the backend.

At the end it prints where everything runs:

| What | Where |
|---|---|
| App | http://localhost:3000, log in as `demo@example.com` / `demo-password-123` |
| Backend API docs | http://localhost:8000/docs |
| Supabase Studio | http://127.0.0.1:54323 |
| Demo API key | printed, together with a ready-to-run `curl` tool call |

The first run takes a few minutes (Docker images, npm packages); later runs take under a minute. Stop everything with
`./quickstart.sh stop`; the database is kept.

- Tools with an API key or no auth work right away. The chat, agent and flows need an
  [OpenRouter](https://openrouter.ai/keys) key: run `OPENROUTER_API_KEY=... ./quickstart.sh` before `.env` exists, or
  add it to `.env` and `main/.env.local` later.
- OAuth integrations (Slack, Notion, …) also need your own OAuth app credentials in `.env`.
- If another local Supabase project already uses the default ports, the script runs this one on ports 544xx and
  prints the actual URLs.

## Getting started

The sections below are the manual version of what `./quickstart.sh` does.

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for the frontend)
- [Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started) for a local database,
  or a hosted Supabase project
- An [OpenRouter](https://openrouter.ai/keys) API key (every model call goes through OpenRouter)

### Database

The schema lives in [`supabase/migrations`](supabase/migrations) and the tool catalog (79 integrations, ~930 actions,
OAuth scopes) in [`supabase/seed.sql`](supabase/seed.sql).

**Local (recommended):**

```bash
supabase start            # first run pulls images; applies migrations + seed.sql
supabase status -o env    # URLs and keys for the .env files
```

Use the legacy JWT keys from `supabase status -o env`: `ANON_KEY` and `SERVICE_ROLE_KEY`. The new `sb_publishable_…` /
`sb_secret_…` keys are rejected by the pinned `supabase` Python client. `supabase db reset` wipes the local database and
re-applies everything. Studio runs at `http://127.0.0.1:54323`.

`port is already allocated` means another local Supabase project uses the default ports: stop it with
`supabase stop --project-id <name>` (its data is kept), or see
[Running multiple local projects](https://supabase.com/docs/guides/local-development/running-multiple-local-projects).

**Hosted Supabase project:**

```bash
supabase link --project-ref <your-project-ref>
supabase db push --include-seed
```

Or run the files from `supabase/migrations/` (in order) and then `supabase/seed.sql` in the SQL Editor.

**Plain PostgreSQL 15+ with psql (no Supabase, e.g. for a quick check or CI):**

```bash
supabase/psql/test.sh                     # throwaway local cluster, removed afterwards (needs initdb 15+)
supabase/psql/test.sh postgresql://...    # or an existing empty database
```

It applies [`supabase/psql/bootstrap.sql`](supabase/psql/bootstrap.sql) (the Supabase roles and `auth` helpers), then the
migrations and `seed.sql` twice to check idempotency. It finishes with RLS smoke checks run as `anon`, two users and
`service_role`, inside a transaction that is rolled back.

Billing views read Stripe data from a `stripe` schema. The baseline migration creates empty placeholder tables there; to
show real subscriptions, replace them with the [Supabase Stripe Wrapper](https://supabase.com/docs/guides/database/extensions/wrappers/stripe).

### Configuration

1. Backend: `cp .env.example .env` and fill in the **REQUIRED** section.
2. Frontend: `cp main/.env.example main/.env.local` and fill in the **REQUIRED** section.
3. Never commit real `.env` files — they are git-ignored.

With local Supabase the backend runs in Docker, so it reaches the database at `http://host.docker.internal:54321`.
The frontend runs on the host and uses `http://127.0.0.1:54321`.

Everything in the **OPTIONAL** sections can stay empty: only the integrations and features you configure will work.

### Tool catalog

`supabase/seed.sql` is generated; don't edit it by hand. Its sources:

- the integrations registered in `INTEGRATION_ROUTERS` (`aci_server/main.py`): input/output schemas, `examples.yaml`,
  `component.json`;
- [`aci_server/db/scripts/catalog.json`](aci_server/db/scripts/catalog.json): name, description, category, auth method,
  logo, custom auth fields, OAuth scopes and which scopes each action needs.

```bash
# regenerate supabase/seed.sql after changing an integration or catalog.json
docker-compose run --rm --no-deps -v "$PWD/supabase:/supabase" aci_server python db/scripts/seed_tools.py --sql /supabase/seed.sql

# validate only
docker-compose run --rm --no-deps aci_server python db/scripts/seed_tools.py --dry-run

# upsert the catalog into the database from .env (SUPABASE_URL / SUPABASE_SERVICE_KEY) without resetting it
docker-compose run --rm --no-deps aci_server python db/scripts/seed_tools.py            # all integrations
docker-compose run --rm --no-deps aci_server python db/scripts/seed_tools.py slack exa  # only some
```

Seeding is idempotent and never deletes rows. Actions of an OAuth integration are enabled for a user only if they
are listed in that integration's `action_scopes`.

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

See [CONTRIBUTING.md](CONTRIBUTING.md#adding-an-integration).

## Contributing & security

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). To report a vulnerability, follow [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
