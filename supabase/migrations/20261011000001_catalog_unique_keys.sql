-- Natural keys for the tool catalog, so aci_server/db/scripts/seed_tools.py and supabase/seed.sql can upsert
-- idempotently. Duplicate scopes (same provider + scope_id) are merged into the oldest row first.

UPDATE "public"."provider_action_scopes" pas
SET "scope_id" = keep."keep_id"
FROM (
    SELECT "id", min("id") OVER (PARTITION BY "provider_id", "scope_id") AS "keep_id"
    FROM "public"."provider_scopes"
) keep
WHERE pas."scope_id" = keep."id" AND keep."id" <> keep."keep_id";

DELETE FROM "public"."provider_scopes" ps
USING "public"."provider_scopes" older
WHERE ps."provider_id" = older."provider_id" AND ps."scope_id" = older."scope_id" AND ps."id" > older."id";

DELETE FROM "public"."provider_action_scopes" pas
USING "public"."provider_action_scopes" older
WHERE pas."action_id" = older."action_id" AND pas."scope_id" = older."scope_id" AND pas."id" > older."id";

ALTER TABLE "public"."provider_actions"
    ADD CONSTRAINT "provider_actions_provider_id_action_slug_key" UNIQUE ("provider_id", "action_slug");

ALTER TABLE "public"."provider_scopes"
    ADD CONSTRAINT "provider_scopes_provider_id_scope_id_key" UNIQUE ("provider_id", "scope_id");

ALTER TABLE "public"."provider_action_scopes"
    ADD CONSTRAINT "provider_action_scopes_action_id_scope_id_key" UNIQUE ("action_id", "scope_id");

ALTER TABLE "public"."provider_tools"
    ADD CONSTRAINT "provider_tools_provider_id_tool_name_key" UNIQUE ("provider_id", "tool_name");
