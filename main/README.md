# VeyraX web app

Next.js 14 (App Router) frontend for VeyraX: landing pages, dashboard, integrations catalog,
OAuth connection flows, agent playground, flows, MCP deployment and billing.

See the [root README](../readme.md) for the project overview and backend setup.

## Getting started

```bash
cp .env.example .env.local   # fill in at least the "Required" section
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The backend (`aci_server`) is expected at `NEXT_PUBLIC_API_URL`
(default `http://localhost:8000`).

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start the dev server |
| `npm run build` | Production build |
| `npm run start` | Serve the production build |
| `npm run lint` | Lint with `next lint` |

## Structure

| Path | Description |
|---|---|
| `app/(landing)`, `app/(auth)`, `app/(app)` | Route groups: marketing pages, sign-in/up, authenticated dashboard |
| `app/api/oauth/<provider>` | OAuth start/callback routes for every OAuth integration |
| `app/api/*` | Server routes: chat, flows, integrations, MCP deploy, Stripe webhooks, email |
| `app/modules/<feature>` | Feature modules (agent, flows, integrations, deploy, settings, landing, ...) |
| `components/ui` | Shared UI components (shadcn/ui based) |
| `lib` | Server actions, AI helpers, database clients, utilities |
| `public` | Static assets: logos, landing images, demo videos |
