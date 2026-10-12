# Contributing to VeyraX

Thanks for your interest in contributing! Bug reports, new integrations, fixes and docs improvements are all welcome.

## Ways to contribute

- **Report a bug** — open an issue using the *Bug report* template.
- **Request an integration or feature** — open an issue using the *Feature / integration request* template.
- **Send a pull request** — for anything bigger than a small fix, open an issue first so we can agree on the approach.
- **Security issues** — do **not** open a public issue, see [SECURITY.md](SECURITY.md).

## Development setup

The fastest way is `./quickstart.sh` (see [Quickstart](readme.md#quickstart)); it does all of the steps below and runs
a smoke test. Manually:

```bash
supabase start                       # local Postgres + Auth with schema and tool catalog
cp .env.example .env                 # fill in the REQUIRED section
cp main/.env.example main/.env.local # fill in the REQUIRED section
docker-compose up --build            # backend on :8000
cd main && npm install && npm run dev # frontend on :3000
```

## Adding an integration

Every integration lives in its own folder in [`aci_server/integrations/`](aci_server/integrations) and follows the same
layered structure. [`openweather`](aci_server/integrations/openweather) and [`exa`](aci_server/integrations/exa) are good,
small references.

```
aci_server/integrations/<name>/
├── client.py        # low-level HTTP calls to the third-party API
├── service.py       # business logic and data transformation
├── route.py         # FastAPI router: validation + wiring, no logic
├── schema.py        # Pydantic input/output models
├── examples.yaml    # request/response examples used in docs and prompts
├── component.json   # optional UI component for rendering results
└── tests.py         # integration tests
```

Conventions:

1. **POST only, params in the body.** Routes are `/<name>/<operation>` (e.g. `/exa/search`), no path parameters.
2. **Validate input and output with Pydantic.** Decorate each route with
   `@schema(input_schema_class=..., output_schema_class=..., examples=examples["/<name>/<operation>"])`
   and unpack params with `Model(**params)`.
3. **Keep routes thin.** All logic goes to `service.py`; all HTTP goes to `client.py`.
4. **Centralized errors.** Call `apply_error_handler_to_service(service)` and `apply_error_handler_to_router(router)`
   instead of try/except in every route.
5. **Unified response.** Return `ApiResponse(data=..., component=...)`; list models use an `items` field.
6. **API-key integrations** expose a `/validate_key` route returning `{"valid": bool, "message": str}`.
7. **Never hardcode credentials** — read them from the user's stored tokens or from environment variables.

Then:

- Register the router in `INTEGRATION_ROUTERS` in [`aci_server/main.py`](aci_server/main.py).
- Add an entry keyed by the router tag to [`aci_server/db/scripts/catalog.json`](aci_server/db/scripts/catalog.json):
  `name`, `description`, `categories`, `auth_method` (`oauth`, `api_key`, `api_key_with_base`, `db_access`, `custom`,
  `none`, `whatsapp-qr`) and `logo_url` (put the file in `main/public/provider-logos/`). Optional: `auth_schema`
  (form fields for `custom` auth), `action_names` (display names), and for OAuth `scopes` + `action_scopes`. OAuth
  actions missing from `action_scopes` are never enabled for users.
- Regenerate the seed and commit it together with your change:
  `docker-compose run --rm --no-deps -v "$PWD/supabase:/supabase" aci_server python db/scripts/seed_tools.py --sql /supabase/seed.sql`
  (run `--dry-run` first to see validation errors), then `supabase db reset` to load it locally.
- If the integration uses OAuth, add start/callback routes in `main/app/api/oauth/<name>/`.
- Add any new environment variables to `.env.example` (and `main/.env.example` if the frontend needs them).
- Add a row to the [Integrations](readme.md#integrations) table in the README.

The full style guide with examples is in [`.cursor/rules/integration_rules.mdc`](.cursor/rules/integration_rules.mdc),
[`component_design.mdc`](.cursor/rules/component_design.mdc) and [`examples_rules.mdc`](.cursor/rules/examples_rules.mdc).

## Tests

Integration tests call the real third-party APIs, so they need valid credentials in `.env`.

```bash
docker-compose exec aci_server /app/run_tests.sh           # all integrations
docker-compose exec aci_server /app/run_tests.sh <name>    # one integration
```

## Pull requests

- Keep PRs focused: one integration or one fix per PR.
- Make sure the backend starts and the tests for the integrations you touched pass.
- Run `npm run lint` in `main/` if you changed the frontend.
- Never commit `.env` files, API keys, tokens, logs or personal data. Use placeholders such as `your-api-key` in examples.
- Describe what changed and how you tested it in the PR template.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
