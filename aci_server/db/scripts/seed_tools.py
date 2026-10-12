"""Seed the tool catalog: providers, provider_actions, provider_scopes, provider_action_scopes, provider_tools.

Rows are built from the integrations registered in main.INTEGRATION_ROUTERS (schemas, examples.yaml,
component.json) plus metadata in db/scripts/catalog.json (names, auth, logos, OAuth scopes).

    python db/scripts/seed_tools.py               # upsert into SUPABASE_URL with SUPABASE_SERVICE_KEY
    python db/scripts/seed_tools.py slack exa     # only these tags
    python db/scripts/seed_tools.py --dry-run     # validate and print a summary, write nothing
    python db/scripts/seed_tools.py --sql PATH    # write SQL (supabase/seed.sql) to PATH, '-' for stdout

Re-running is safe: everything is upserted on natural keys. Rows of removed integrations/actions are kept.
"""
import argparse
import ast
import contextlib
import importlib
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
load_dotenv()

with contextlib.redirect_stdout(sys.stderr):
    from db.supabase import get_supabase  # noqa: E402
    from integrations.common.utils import get_router_tools  # noqa: E402

CATALOG_PATH = Path(__file__).with_name("catalog.json")
INTEGRATIONS_DIR = ROOT / "integrations"
SKIP_ACTIONS = {"validate_key"}
AUTH_METHODS = {"oauth", "api_key", "api_key_with_base", "db_access", "custom", "none", "whatsapp-qr"}
REQUIRED_FIELDS = ("name", "description", "auth_method", "logo_url")


def log(*args):
    print(*args, file=sys.stderr)


def load_integration_routers():
    """Read INTEGRATION_ROUTERS from main.py without importing it (main needs every service configured)."""
    tree = ast.parse((ROOT / "main.py").read_text())
    imports = {alias.asname or alias.name: (node.module, alias.name) for node in tree.body if isinstance(node, ast.ImportFrom) for alias in node.names}
    mapping = next(
        node.value for node in tree.body
        if isinstance(node, ast.Assign) and any(getattr(target, "id", None) == "INTEGRATION_ROUTERS" for target in node.targets)
    )
    routers = {}
    for key, value in zip(mapping.keys, mapping.values):
        module, name = imports[value.id]
        routers[key.value] = getattr(importlib.import_module(module), name)
    return routers


def alt_tag(tag):
    return tag.replace("-", "_") if "-" in tag else tag.replace("_", "-")


def to_json(value):
    return json.loads(json.dumps(value, default=str))


def parse_json(value):
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def load_components(tag):
    for folder in (tag, alt_tag(tag)):
        path = INTEGRATIONS_DIR / folder / "component.json"
        if path.exists():
            data = json.loads(path.read_text())
            items = data.items() if isinstance(data, dict) else ((c.get("name"), c) for c in data)
            return {
                endpoint.split("/")[-1]: {name: component}
                for name, component in items
                if isinstance(component, dict)
                for endpoint in component.get("related_endpoints") or []
                if endpoint
            }
    return {}


def normalize_examples(examples):
    result = []
    for example in examples or []:
        if not isinstance(example, dict):
            continue
        entry = {"scenario": example.get("scenario", ""), "description": example.get("description", "")}
        for key in ("input", "output"):
            value = example.get(f"{key}_json", example.get(key))
            if value is not None:
                entry[key] = parse_json(value)
        result.append(entry)
    return result


def build_actions(tag, router, names=None):
    components = load_components(tag)
    actions = {}
    for spec in get_router_tools(router):
        function = dict(spec["function"])
        slug = function["name"].split("/")[-1]
        if slug in SKIP_ACTIONS:
            continue
        output_schema = function.pop("output_schema", {})
        actions[slug] = {
            "action_slug": slug,
            "action_name": (names or {}).get(slug) or slug.replace("_", " ").replace("-", " ").title(),
            "input_schema": {"type": spec.get("type", "function"), "function": function},
            "output_schema": output_schema,
            "examples": normalize_examples(spec.get("examples")),
            "ui_component": components.get(slug),
        }
    return to_json(list(actions.values()))


def build_provider(tag, router, entry):
    """All rows for one provider, keyed by natural keys (provider_tag, action_slug, scope_id)."""
    errors, warnings = [], []
    missing = [field for field in REQUIRED_FIELDS if not entry.get(field)]
    if missing:
        errors.append(f"missing {', '.join(missing)}")
    if entry.get("auth_method") not in AUTH_METHODS:
        errors.append(f"auth_method must be one of {sorted(AUTH_METHODS)}")

    actions = build_actions(tag, router, entry.get("action_names"))
    slugs = [action["action_slug"] for action in actions]
    scopes = entry.get("scopes") or {}
    action_scopes = entry.get("action_scopes") or {}
    for slug in set(entry.get("action_names") or {}) - set(slugs):
        warnings.append(f"action_names: unknown action {slug!r}")
    for slug, required in action_scopes.items():
        if slug not in slugs:
            warnings.append(f"action_scopes: unknown action {slug!r}")
        for scope in set(required) - set(scopes):
            errors.append(f"action_scopes[{slug!r}]: scope {scope!r} is not listed in scopes")
    tools = entry.get("legacy_tools") or []
    tool_names = [tool["tool_name"] for tool in tools]
    if len(tool_names) != len(set(tool_names)):
        errors.append("legacy_tools: duplicate tool_name")
    if entry.get("auth_method") == "oauth":
        unmapped = [slug for slug in slugs if slug not in action_scopes]
        if unmapped:
            warnings.append(f"OAuth actions without action_scopes are never enabled for users: {', '.join(unmapped)}")

    provider = {
        "provider_tag": tag,
        "name": entry.get("name"),
        "description": entry.get("description"),
        "categories": entry.get("categories"),
        "auth_method": entry.get("auth_method"),
        "auth_schema": entry.get("auth_schema"),
        "logo_url": entry.get("logo_url"),
        "is_enabled": entry.get("is_enabled", True),
        "is_rentable": False,
        "has_index_capability": False,
        "created_at": entry.get("created_at"),
    }
    return {
        "provider": provider,
        "actions": actions,
        "scopes": [{"scope_id": scope_id, "scope_name": name} for scope_id, name in scopes.items()],
        "links": [(slug, scope) for slug, required in action_scopes.items() if slug in slugs for scope in required],
        "tools": tools,
        "errors": errors,
        "warnings": warnings,
    }


def build_catalog(routers, catalog, tags):
    built = {}
    for tag in tags:
        if tag not in catalog:
            built[tag] = {"errors": [f"no entry in {CATALOG_PATH.name}; add one (see CONTRIBUTING.md)"], "warnings": []}
            continue
        with contextlib.redirect_stdout(sys.stderr):
            built[tag] = build_provider(tag, routers[tag], catalog[tag])
    return built


# ---------- SQL output (supabase/seed.sql) ----------

def sql_literal(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return "'" + value.replace("'", "''") + "'"


def sql_values(rows):
    return ",\n".join("  (" + ", ".join(sql_literal(value) for value in row) + ")" for row in rows)


def render_sql(built):
    providers = [b["provider"] for b in built.values()]
    actions = [(tag, *(a[k] for k in ("action_slug", "action_name", "input_schema", "output_schema", "examples", "ui_component"))) for tag, b in built.items() for a in b["actions"]]
    scopes = [(tag, s["scope_id"], s["scope_name"]) for tag, b in built.items() for s in b["scopes"]]
    links = [(tag, slug, scope) for tag, b in built.items() for slug, scope in b["links"]]
    tools = [(tag, t["tool_name"], t.get("require_scope"), t.get("require_index"), t.get("scopes")) for tag, b in built.items() for t in b["tools"]]

    parts = [
        "-- Tool catalog seed. Generated by aci_server/db/scripts/seed_tools.py --sql; do not edit by hand.",
        "-- Sources: integrations registered in aci_server/main.py and aci_server/db/scripts/catalog.json.",
        "-- Applied automatically by `supabase start` / `supabase db reset`. Safe to re-run.",
        "",
        "insert into public.providers (provider_tag, name, description, categories, auth_method, auth_schema, logo_url, is_enabled, is_rentable, has_index_capability, created_at)",
        "select v.provider_tag, v.name, v.description, v.categories, v.auth_method,",
        "  (select array_agg(e) from jsonb_array_elements(v.auth_schema::jsonb) e),",
        "  v.logo_url, v.is_enabled::boolean, v.is_rentable::boolean, v.has_index_capability::boolean,",
        "  coalesce(v.created_at::bigint, extract(epoch from now())::bigint)",
        "from (values",
        sql_values([(p["provider_tag"], p["name"], p["description"], p["categories"], p["auth_method"], p["auth_schema"], p["logo_url"], p["is_enabled"], p["is_rentable"], p["has_index_capability"], p["created_at"]) for p in providers]),
        ") as v(provider_tag, name, description, categories, auth_method, auth_schema, logo_url, is_enabled, is_rentable, has_index_capability, created_at)",
        "on conflict (provider_tag) do update set name = excluded.name, description = excluded.description, categories = excluded.categories,",
        "  auth_method = excluded.auth_method, auth_schema = excluded.auth_schema, logo_url = excluded.logo_url, is_enabled = excluded.is_enabled;",
        "",
        "insert into public.provider_actions (provider_id, action_slug, action_name, input_schema, output_schema, examples, ui_component)",
        "select p.id, v.action_slug, v.action_name, v.input_schema::jsonb, v.output_schema::jsonb, v.examples::jsonb, v.ui_component::jsonb",
        "from (values",
        sql_values(actions),
        ") as v(provider_tag, action_slug, action_name, input_schema, output_schema, examples, ui_component)",
        "join public.providers p on p.provider_tag = v.provider_tag",
        "on conflict (provider_id, action_slug) do update set action_name = excluded.action_name, input_schema = excluded.input_schema,",
        "  output_schema = excluded.output_schema, examples = excluded.examples, ui_component = excluded.ui_component;",
    ]
    if scopes:
        parts += [
            "",
            "insert into public.provider_scopes (provider_id, scope_id, scope_name)",
            "select p.id, v.scope_id, v.scope_name",
            "from (values",
            sql_values(scopes),
            ") as v(provider_tag, scope_id, scope_name)",
            "join public.providers p on p.provider_tag = v.provider_tag",
            "on conflict (provider_id, scope_id) do update set scope_name = excluded.scope_name;",
        ]
    if links:
        parts += [
            "",
            "insert into public.provider_action_scopes (action_id, scope_id)",
            "select a.id, s.id",
            "from (values",
            sql_values(links),
            ") as v(provider_tag, action_slug, scope_id)",
            "join public.providers p on p.provider_tag = v.provider_tag",
            "join public.provider_actions a on a.provider_id = p.id and a.action_slug = v.action_slug",
            "join public.provider_scopes s on s.provider_id = p.id and s.scope_id = v.scope_id",
            "on conflict (action_id, scope_id) do nothing;",
        ]
    if tools:
        parts += [
            "",
            "insert into public.provider_tools (provider_id, tool_name, require_scope, require_index, scopes)",
            "select p.id, v.tool_name, v.require_scope::boolean, v.require_index::boolean, v.scopes",
            "from (values",
            sql_values(tools),
            ") as v(provider_tag, tool_name, require_scope, require_index, scopes)",
            "join public.providers p on p.provider_tag = v.provider_tag",
            "on conflict (provider_id, tool_name) do update set require_scope = excluded.require_scope,",
            "  require_index = excluded.require_index, scopes = excluded.scopes;",
        ]
    return "\n".join(parts) + "\n"


# ---------- REST output (any Supabase project) ----------

def seed_rest(supabase, built):
    providers = [{**b["provider"], "created_at": b["provider"]["created_at"] or int(time.time())} for b in built.values()]
    provider_ids = {
        row["provider_tag"]: row["id"]
        for row in supabase.table("providers").upsert(providers, on_conflict="provider_tag").execute().data
    }
    for tag, b in built.items():
        provider_id = provider_ids[tag]
        action_ids = {}
        if b["actions"]:
            rows = supabase.table("provider_actions").upsert(
                [{**action, "provider_id": provider_id} for action in b["actions"]], on_conflict="provider_id,action_slug"
            ).execute().data
            action_ids = {row["action_slug"]: row["id"] for row in rows}
        if b["scopes"]:
            rows = supabase.table("provider_scopes").upsert(
                [{**scope, "provider_id": provider_id} for scope in b["scopes"]], on_conflict="provider_id,scope_id"
            ).execute().data
            scope_ids = {row["scope_id"]: row["id"] for row in rows}
            links = [{"action_id": action_ids[slug], "scope_id": scope_ids[scope]} for slug, scope in b["links"]]
            if links:
                supabase.table("provider_action_scopes").upsert(links, on_conflict="action_id,scope_id", ignore_duplicates=True).execute()
        if b["tools"]:
            supabase.table("provider_tools").upsert(
                [{"provider_id": provider_id, "tool_name": t["tool_name"], "require_scope": t.get("require_scope"),
                  "require_index": t.get("require_index"), "scopes": t.get("scopes")} for t in b["tools"]],
                on_conflict="provider_id,tool_name",
            ).execute()


def main():
    parser = argparse.ArgumentParser(description="Seed the Supabase tool catalog from aci_server/main.py and db/scripts/catalog.json")
    parser.add_argument("tags", nargs="*", help="Provider tags to seed (default: all registered integrations)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate and print a summary without writing anything")
    mode.add_argument("--sql", metavar="PATH", help="Write the seed as SQL to PATH (supabase/seed.sql), '-' for stdout")
    args = parser.parse_args()

    with contextlib.redirect_stdout(sys.stderr):
        routers = load_integration_routers()
    unknown = set(args.tags) - routers.keys()
    if unknown:
        parser.error(f"unknown tags: {', '.join(sorted(unknown))}")
    if args.sql and args.tags:
        parser.error("--sql always renders the whole catalog; drop the tag arguments")

    catalog = json.loads(CATALOG_PATH.read_text())
    tags = args.tags or sorted(routers)
    built = build_catalog(routers, catalog, tags)

    for tag in sorted(set(catalog) - routers.keys()):
        log(f"warning: {CATALOG_PATH.name} entry {tag!r} has no router in main.INTEGRATION_ROUTERS; ignored")
    for tag, b in built.items():
        for message in b["warnings"]:
            log(f"warning: {tag}: {message}")
        if "provider" in b:
            log(f"{tag:<16} {b['provider']['auth_method']:<18} {len(b['actions']):>3} actions  {len(b['scopes']):>2} scopes  {len(b['links']):>3} scope links")
    errors = [f"{tag}: {message}" for tag, b in built.items() for message in b["errors"]]
    if errors:
        log("\n".join(["", "Catalog errors:"] + errors))
        sys.exit(1)

    totals = f"{len(built)} providers, {sum(len(b['actions']) for b in built.values())} actions"
    if args.sql:
        sql = render_sql(built)
        if args.sql == "-":
            sys.stdout.write(sql)
        else:
            Path(args.sql).write_text(sql)
        log(f"\nWrote SQL for {totals} to {args.sql}")
    elif args.dry_run:
        log(f"\nValid: {totals} (dry run, nothing written)")
    else:
        seed_rest(get_supabase(), built)
        log(f"\nSeeded {totals}")


if __name__ == "__main__":
    main()
