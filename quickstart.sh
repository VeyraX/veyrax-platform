#!/usr/bin/env bash
# One-command local setup: Supabase (schema + tool catalog), .env files, backend, frontend, smoke test.
#
#   ./quickstart.sh          start everything (safe to re-run) and run a smoke test
#   ./quickstart.sh stop     stop everything (database data is kept)
#
# Optional: OPENAI_API_KEY=... OPENROUTER_API_KEY=... ./quickstart.sh  (written into freshly created .env files;
# needed for the agent, chat and flows, not for calling tools).
set -euo pipefail
trap 'printf "\033[31mquickstart.sh failed on line %s\033[0m\n" "$LINENO" >&2' ERR

cd "$(dirname "${BASH_SOURCE[0]}")"
STATE_DIR=.quickstart
SHIFTED_WORKDIR=.supabase-local
DEMO_EMAIL=demo@example.com
DEMO_PASSWORD=demo-password-123

say() { printf '\033[1m==> %s\033[0m\n' "$*"; }
die() {
  printf '\033[31mError: %s\033[0m\n' "$*" >&2
  exit 1
}
port_busy() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }
sb() {
  if [[ -d "$SHIFTED_WORKDIR" ]]; then
    supabase --workdir "$SHIFTED_WORKDIR" "$@"
  else
    supabase "$@"
  fi
}
compose() {
  if docker compose version &>/dev/null; then
    docker compose "$@"
  else
    docker-compose "$@"
  fi
}
wait_for() { # url, name, seconds
  local i
  for ((i = 0; i < $3; i++)); do
    if curl -s -o /dev/null --max-time 5 "$1"; then return 0; fi
    sleep 1
  done
  die "$2 did not come up at $1 (see the logs above or in $STATE_DIR/)"
}

stop() {
  if [[ -f "$STATE_DIR/frontend.pid" ]]; then
    say "Stopping frontend"
    kill "$(cat "$STATE_DIR/frontend.pid")" 2>/dev/null || true
    rm -f "$STATE_DIR/frontend.pid"
  fi
  say "Stopping backend"
  compose down
  say "Stopping Supabase (data is kept)"
  sb stop
}

if [[ "${1:-}" == "stop" ]]; then
  stop
  exit 0
elif [[ $# -gt 0 ]]; then
  die "usage: ./quickstart.sh [stop]"
fi

say "Checking prerequisites"
for tool in docker supabase node npm curl; do
  command -v "$tool" &>/dev/null || die "'$tool' is not installed (see readme.md#quickstart)"
done
docker info &>/dev/null || die "Docker is not running"
docker compose version &>/dev/null || command -v docker-compose &>/dev/null || die "Docker Compose is not installed"
node -e 'process.exit(+process.versions.node.split(".")[0] >= 18 ? 0 : 1)' || die "Node.js 18+ is required"
mkdir -p "$STATE_DIR"

say "Starting Supabase (first run downloads images and loads the tool catalog)"
if [[ ! -d "$SHIFTED_WORKDIR" ]] && ! supabase status &>/dev/null && port_busy 54321; then
  echo "Port 54321 is used by another local Supabase project; running this one on ports 544xx instead."
  mkdir -p "$SHIFTED_WORKDIR/supabase"
fi
if [[ -d "$SHIFTED_WORKDIR" ]]; then
  sed -E 's/= 543([0-9]{2})/= 544\1/' supabase/config.toml >"$SHIFTED_WORKDIR/supabase/config.toml"
  ln -sfn ../../supabase/migrations "$SHIFTED_WORKDIR/supabase/migrations"
  ln -sfn ../../supabase/seed.sql "$SHIFTED_WORKDIR/supabase/seed.sql"
fi
sb start
eval "$(sb status -o env | grep -E '^(API_URL|ANON_KEY|SERVICE_ROLE_KEY|STUDIO_URL|MAILPIT_URL)=')"
API_PORT="${API_URL##*:}"

say "Writing .env and main/.env.local (existing files are kept)"
API_PORT="$API_PORT" ANON_KEY="$ANON_KEY" SERVICE_ROLE_KEY="$SERVICE_ROLE_KEY" node <<'NODE'
const fs = require("fs");
const env = process.env;
const encryptionKey = require("crypto").randomBytes(32).toString("hex");
const backendUrl = `http://host.docker.internal:${env.API_PORT}`;
const llm = { OPENAI_API_KEY: env.OPENAI_API_KEY || "", OPENROUTER_API_KEY: env.OPENROUTER_API_KEY || "" };
function fill(src, dst, values) {
  if (fs.existsSync(dst)) {
    const current = (fs.readFileSync(dst, "utf8").match(/^SUPABASE_URL=(.*)$/m) || [])[1];
    console.log(current === values.SUPABASE_URL ? `${dst} exists, keeping it`
      : `WARNING: keeping existing ${dst}, but its SUPABASE_URL (${current}) is not the local ${values.SUPABASE_URL}; move it away to regenerate`);
    return;
  }
  let text = fs.readFileSync(src, "utf8");
  for (const [key, value] of Object.entries(values)) {
    const re = new RegExp(`^${key}=.*$`, "m");
    if (!re.test(text)) throw new Error(`${key} not found in ${src}`);
    text = text.replace(re, `${key}=${value}`);
  }
  fs.writeFileSync(dst, text, { mode: 0o600 });
  console.log(`created ${dst}`);
}
fill(".env.example", ".env", {
  ENCRYPTION_KEY: encryptionKey,
  SUPABASE_URL: backendUrl,
  SUPABASE_SERVICE_KEY: env.SERVICE_ROLE_KEY,
  NEXT_PUBLIC_SUPABASE_ANON_KEY: env.ANON_KEY,
  // fild/ creates a Supabase client at import time; point it at the local project so the server starts
  FILD_SUPABASE_URL: backendUrl,
  FILD_SUPABASE_SERVICE_KEY: env.SERVICE_ROLE_KEY,
  ...llm,
});
fill("main/.env.example", "main/.env.local", {
  NEXT_PUBLIC_SUPABASE_URL: `http://127.0.0.1:${env.API_PORT}`,
  NEXT_PUBLIC_SUPABASE_ANON_KEY: env.ANON_KEY,
  SUPABASE_URL: `http://127.0.0.1:${env.API_PORT}`,
  SUPABASE_SERVICE_KEY: env.SERVICE_ROLE_KEY,
  ENCRYPTION_KEY: encryptionKey,
  ...llm,
});
NODE

say "Starting backend (docker compose)"
compose up -d --build
wait_for http://localhost:8000/ "Backend" 180

say "Starting frontend"
if [[ -f "$STATE_DIR/frontend.pid" ]] && kill -0 "$(cat "$STATE_DIR/frontend.pid")" 2>/dev/null; then
  echo "already running"
else
  port_busy 3000 && die "Port 3000 is already in use; stop that process and re-run"
  # puppeteer is a dependency but unused by the app; skip its ~150 MB Chrome download
  if [[ ! -d main/node_modules/next ]]; then (cd main && PUPPETEER_SKIP_DOWNLOAD=1 npm ci --no-audit --no-fund); fi
  (cd main && exec node node_modules/next/dist/bin/next dev) >"$STATE_DIR/frontend.log" 2>&1 </dev/null &
  echo $! >"$STATE_DIR/frontend.pid"
fi
wait_for http://localhost:3000/login "Frontend" 180

say "Smoke test: demo user -> API key -> connect Hacker News -> call a tool through the backend"
SMOKE="$(SB_URL="http://127.0.0.1:$API_PORT" ANON_KEY="$ANON_KEY" EMAIL="$DEMO_EMAIL" PASSWORD="$DEMO_PASSWORD" node <<'NODE'
const { SB_URL, ANON_KEY, EMAIL, PASSWORD } = process.env;
async function call(url, { token, body, method = body ? "POST" : "GET", headers = {} } = {}) {
  const res = await fetch(url, {
    method,
    headers: { apikey: ANON_KEY, Authorization: `Bearer ${token || ANON_KEY}`, "Content-Type": "application/json", ...headers },
    body: body && JSON.stringify(body),
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`${method} ${url} -> ${res.status} ${text.slice(0, 300)}`);
  return text ? JSON.parse(text) : null;
}
(async () => {
  const credentials = { email: EMAIL, password: PASSWORD };
  let session;
  try {
    session = await call(`${SB_URL}/auth/v1/token?grant_type=password`, { body: credentials });
  } catch {
    session = await call(`${SB_URL}/auth/v1/signup`, { body: credentials });
  }
  const token = session.access_token, userId = session.user.id;
  const rest = (path, options) => call(`${SB_URL}/rest/v1/${path}`, { token, ...options });
  let [key] = await rest(`users_api_keys?select=api_key&user_id=eq.${userId}`);
  if (!key) [key] = await rest("users_api_keys", { body: { user_id: userId, api_key: require("crypto").randomUUID() }, headers: { Prefer: "return=representation" } });
  const [provider] = await rest("providers?select=id&provider_tag=eq.hacker-news");
  const ignoreDuplicates = { Prefer: "resolution=ignore-duplicates" };
  await rest("users_providers?on_conflict=provider_id,user_id", { body: { user_id: userId, provider_id: provider.id }, headers: ignoreDuplicates });
  const actions = await rest(`provider_actions?select=id&provider_id=eq.${provider.id}`);
  await rest("users_provider_actions?on_conflict=user_id,action_id", { body: actions.map((a) => ({ user_id: userId, action_id: a.id })), headers: ignoreDuplicates });
  const result = await call("http://localhost:8000/tool-call/hacker-news/top_stories", { body: { limit: 1 }, headers: { VEYRAX_API_KEY: key.api_key, Authorization: "" } });
  const story = result.data.stories[0];
  console.log(`API_KEY=${key.api_key}`);
  console.log(`STORY=${story.title}`);
})().catch((error) => { console.error(error.message); process.exit(1); });
NODE
)" || die "Smoke test failed (backend logs: docker compose logs aci_server)"
DEMO_API_KEY="$(sed -n 's/^API_KEY=//p' <<<"$SMOKE")"
echo "Backend returned the top Hacker News story: $(sed -n 's/^STORY=//p' <<<"$SMOKE")"

cat <<EOF

$(say "VeyraX is running")
  App          http://localhost:3000     log in: $DEMO_EMAIL / $DEMO_PASSWORD
  Backend      http://localhost:8000/docs
  Supabase     $STUDIO_URL  (Studio), emails: $MAILPIT_URL
  Demo API key $DEMO_API_KEY

  Try a tool call:
    curl -X POST http://localhost:8000/tool-call/hacker-news/top_stories \\
      -H 'VEYRAX_API_KEY: $DEMO_API_KEY' -H 'Content-Type: application/json' -d '{"limit": 3}'

  Frontend log: $STATE_DIR/frontend.log    Backend logs: docker compose logs -f aci_server
  Stop everything: ./quickstart.sh stop
EOF
