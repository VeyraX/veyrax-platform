# AGENTS.md

Notes for AI coding agents (and humans) working in this repo. User-facing setup is in [readme.md](readme.md),
contribution rules in [CONTRIBUTING.md](CONTRIBUTING.md).

## Layout

- `aci_server/` — FastAPI backend (Python 3.11, runs in Docker). Integrations: `aci_server/integrations/<name>/`,
  registered in `INTEGRATION_ROUTERS` in `aci_server/main.py`.
- `main/` — Next.js frontend.
- `supabase/` — Supabase CLI project: `config.toml`, `migrations/` (schema), `seed.sql` (tool catalog, generated).

## Running everything locally

`./quickstart.sh` starts Supabase, writes `.env` files, starts backend + frontend and runs an end-to-end smoke test
(non-zero exit on failure). `./quickstart.sh stop` stops it all. Use it to check that a change didn't break the stack.

## LLM calls

Every model call (chat, agents, flows, embeddings, speech-to-text) goes through OpenRouter with `OPENROUTER_API_KEY`.
Model IDs live in one place per app: `aci_server/llm.py` (backend) and `main/lib/ai/openrouter.ts` (frontend), plus the
playground list in `main/app/modules/agent/components/api/models.ts`. Use those helpers instead of creating OpenAI or
Anthropic clients directly; check IDs against https://openrouter.ai/api/v1/models.

## Database

- Local database: `supabase start` (applies `supabase/migrations/*` + `supabase/seed.sql`), `supabase db reset` to rebuild,
  `supabase status -o env` for URLs/keys. Use `ANON_KEY` / `SERVICE_ROLE_KEY` (JWT); `sb_secret_…` keys are rejected
  by the pinned `supabase==2.13.0` Python client.
- From the backend container the local API is `http://host.docker.internal:54321`; from the host it is `http://127.0.0.1:54321`.
- Schema changes: add a new file `supabase/migrations/<YYYYMMDDHHMMSS>_<name>.sql`. Never edit an existing migration.
  Tables in `public` need explicit `GRANT`s to `anon` / `authenticated` / `service_role` (new tables are not
  auto-exposed) and RLS policies.
- `20261011000000_baseline.sql` is a snapshot of the production schema. A database that already has this schema
  (e.g. production) must mark it as applied instead of running it:
  `supabase migration repair --status applied 20261011000000`.

## Tool catalog (providers / provider_actions / scopes)

Sources of truth — edit these, never the database or `supabase/seed.sql` directly:

1. integration code: Pydantic schemas, `examples.yaml`, `component.json` in `aci_server/integrations/<name>/`;
2. `aci_server/db/scripts/catalog.json`: one entry per router tag (name, description, categories, auth_method,
   logo_url, optional auth_schema, action_names, scopes, action_scopes, legacy_tools). Logos go to
   `main/public/provider-logos/`.

After changing either, run from the repo root (requires `.env` to exist, e.g. `cp .env.example .env`):

```bash
docker-compose run --rm --no-deps aci_server python db/scripts/seed_tools.py --dry-run          # validate
docker-compose run --rm --no-deps -v "$PWD/supabase:/supabase" aci_server python db/scripts/seed_tools.py --sql /supabase/seed.sql
supabase db reset                                                                                # load locally
```

`--dry-run` must print no `Catalog errors`; fix every `warning:` you introduced. The `--sql` output is deterministic,
so `git diff supabase/seed.sql` shows exactly what changed. Commit `catalog.json`, `seed.sql` and the code together.

`python db/scripts/seed_tools.py [tags...]` (no flags) upserts into whatever `SUPABASE_URL` points at. Check the
target before running it; it never deletes rows.

## Verification

- Database (migrations + seed + RLS smoke checks, ~2 s, no Supabase needed): `supabase/psql/test.sh`. Run it after
  any change to `supabase/migrations/` or `supabase/seed.sql`; add an assertion there for new RLS-sensitive tables.
- Backend tests call real third-party APIs: `docker-compose exec aci_server /app/run_tests.sh <name>`.
- Frontend: `cd main && npm run lint`.
