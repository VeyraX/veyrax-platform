#!/usr/bin/env bash
# Apply supabase/migrations + supabase/seed.sql to plain PostgreSQL with psql and smoke-test the result.
#
#   supabase/psql/test.sh                       # throwaway local cluster (needs initdb/pg_ctl 15+), removed afterwards
#   supabase/psql/test.sh postgresql://...      # an existing EMPTY database (refuses one that already has the schema)
#
# PG_BIN=/path/to/postgres/bin overrides where initdb/pg_ctl/psql are taken from.
set -euo pipefail

SUPABASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

find_pg_bin() {
  local dir version
  for dir in "${PG_BIN:-}" "$(dirname "$(command -v initdb 2>/dev/null || echo /nonexistent/x)")" \
    /opt/homebrew/opt/postgresql@{17,16,15}/bin /usr/local/opt/postgresql@{17,16,15}/bin \
    /usr/lib/postgresql/{17,16,15}/bin; do
    [[ -n "$dir" && -x "$dir/initdb" && -x "$dir/pg_ctl" ]] || continue
    version="$("$dir/initdb" --version | grep -oE '[0-9]+' | head -1)"
    if ((version >= 15)); then
      echo "$dir"
      return
    fi
  done
  echo "No PostgreSQL 15+ initdb/pg_ctl found; install one or set PG_BIN, or pass a DATABASE_URL." >&2
  exit 1
}

if [[ $# -ge 1 ]]; then
  DB="$1"
  PSQL="${PG_BIN:+$PG_BIN/}psql"
else
  BIN="$(find_pg_bin)"
  PSQL="$BIN/psql"
  TMPROOT="${TMPDIR:-/tmp}"
  TMP="$(mktemp -d "${TMPROOT%/}/veyrax-pg.XXXXXX")"
  trap '"$BIN/pg_ctl" -D "$TMP/data" -m immediate stop &>/dev/null || true; rm -rf "$TMP"' EXIT
  "$BIN/initdb" -D "$TMP/data" -U postgres -A trust -E UTF8 --no-locale >/dev/null
  "$BIN/pg_ctl" -D "$TMP/data" -l "$TMP/postgres.log" -w -o "-k $TMP -c listen_addresses=''" start >/dev/null
  DB="postgresql://postgres@/postgres?host=$TMP"
  echo "Started throwaway PostgreSQL $("$BIN/initdb" --version | grep -oE '[0-9]+\.[0-9]+' | head -1) in $TMP"
fi

run() { "$PSQL" "$DB" -X -q -o /dev/null -v ON_ERROR_STOP=1 "$@"; }
value() { "$PSQL" "$DB" -X -A -t -v ON_ERROR_STOP=1 -c "$1"; }

if [[ "$(value "select to_regclass('public.providers') is not null")" == "t" ]]; then
  echo "Refusing to run: public.providers already exists in this database. Use an empty database." >&2
  exit 1
fi

echo "Applying bootstrap.sql"
run -1 -f "$SUPABASE_DIR/psql/bootstrap.sql"
for migration in "$SUPABASE_DIR"/migrations/*.sql; do
  echo "Applying migrations/$(basename "$migration")"
  run -1 -f "$migration"
done

CATALOG_HASH="select md5(string_agg(row_text, '' order by row_text)) from (
  select p::text as row_text from (select provider_tag, name, description, categories, auth_method, auth_schema, logo_url, is_enabled, created_at from public.providers) p
  union all select a::text from (select p.provider_tag, a.action_slug, a.action_name, a.input_schema, a.output_schema, a.examples, a.ui_component
    from public.provider_actions a join public.providers p on p.id = a.provider_id) a
  union all select s::text from (select p.provider_tag, s.scope_id, s.scope_name from public.provider_scopes s join public.providers p on p.id = s.provider_id) s
  union all select l::text from (select a.action_slug, s.scope_id from public.provider_action_scopes l
    join public.provider_actions a on a.id = l.action_id join public.provider_scopes s on s.id = l.scope_id) l
  union all select t::text from (select p.provider_tag, t.tool_name, t.require_scope, t.require_index, t.scopes
    from public.provider_tools t join public.providers p on p.id = t.provider_id) t
) q"

echo "Applying seed.sql"
run -1 -f "$SUPABASE_DIR/seed.sql"
FIRST="$(value "$CATALOG_HASH")"
echo "Applying seed.sql again (must not change anything)"
run -1 -f "$SUPABASE_DIR/seed.sql"
if [[ "$FIRST" != "$(value "$CATALOG_HASH")" ]]; then
  echo "FAIL: re-applying seed.sql changed the catalog" >&2
  exit 1
fi

echo "Running smoke checks (inside a transaction that is rolled back)"
run <<'SQL'
begin;

do $$
begin
  assert (select count(*) from public.providers) > 0, 'no providers seeded';
  assert not exists (select from public.providers p where not exists (select from public.provider_actions a where a.provider_id = p.id)),
    'a provider has no actions';
  assert not exists (
    select from public.providers p where p.auth_method = 'oauth'
      and not exists (select from public.provider_scopes s join public.provider_action_scopes l on l.scope_id = s.id where s.provider_id = p.id)
  ), 'an OAuth provider has no scope links (its actions can never be enabled)';
end $$;

insert into auth.users (id, email) values
  ('00000000-0000-4000-8000-00000000000a', 'user-a@example.com'),
  ('00000000-0000-4000-8000-00000000000b', 'user-b@example.com');

-- anon: reads the catalog, cannot write it
set local role anon;
select set_config('request.jwt.claims', '{"role":"anon"}', true);
do $$
begin
  assert (select count(*) from public.providers) > 0, 'anon cannot read providers';
  assert (select count(*) from public.provider_actions) > 0, 'anon cannot read provider_actions';
  begin
    insert into public.providers (provider_tag, name, description, logo_url, created_at) values ('x', 'x', 'x', 'x', 1);
    raise exception 'anon could insert into providers';
  exception when insufficient_privilege then null;
  end;
end $$;

-- user A connects Slack and enables its actions through RLS
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-4000-8000-00000000000a","role":"authenticated"}', true);
insert into public.users_providers (user_id, provider_id)
  select auth.uid(), id from public.providers where provider_tag = 'slack';
insert into public.users_provider_actions (user_id, action_id)
  select auth.uid(), a.id from public.provider_actions a join public.providers p on p.id = a.provider_id where p.provider_tag = 'slack';
do $$
declare updated int;
begin
  assert (select count(*) from public.user_actions_view) > 0, 'user A sees no actions in user_actions_view';
  update public.providers set name = 'changed' where provider_tag = 'slack';
  get diagnostics updated = row_count;
  assert updated = 0, 'an authenticated user could update providers';
end $$;

-- user B sees nothing of user A
select set_config('request.jwt.claims', '{"sub":"00000000-0000-4000-8000-00000000000b","role":"authenticated"}', true);
do $$
begin
  assert (select count(*) from public.user_actions_view) = 0, 'user B can see user A actions';
  assert (select count(*) from public.users_providers) = 0, 'user B can see user A providers';
end $$;

-- service role (backend) sees user A's tools; RPC used by the integrations page works
set local role service_role;
select set_config('request.jwt.claims', '{"role":"service_role"}', true);
do $$
begin
  assert (select count(*) from public.user_actions_view where user_id = '00000000-0000-4000-8000-00000000000a') > 0,
    'service_role cannot read user_actions_view';
  assert (select count_of_users from public.get_top_connected_providers() where provider_tag = 'slack') = 1,
    'get_top_connected_providers does not count user A';
end $$;

rollback;
SQL

value "select format('PASS: %s providers, %s actions, %s scopes, %s scope links, %s legacy tools',
  (select count(*) from public.providers), (select count(*) from public.provider_actions), (select count(*) from public.provider_scopes),
  (select count(*) from public.provider_action_scopes), (select count(*) from public.provider_tools))"
