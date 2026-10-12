-- Baseline schema of the VeyraX Supabase database (public schema), taken from the production
-- database with `supabase db dump --schema public` (structure only, no data).
-- Removed from the dump: internal analytics views (user_retention, omi_user_retention,
-- provider_errors_view) and the unused public.exec(sql) helper.


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA IF NOT EXISTS "public";


ALTER SCHEMA "public" OWNER TO "pg_database_owner";


COMMENT ON SCHEMA "public" IS 'standard public schema';


CREATE TYPE "public"."auth_field_type" AS ENUM (
    'text',
    'password',
    'textarea',
    'number',
    'email',
    'url',
    'select',
    'checkbox',
    'tags',
    'json'
);


ALTER TYPE "public"."auth_field_type" OWNER TO "postgres";


COMMENT ON TYPE "public"."auth_field_type" IS 'Field types supported for auth';


CREATE OR REPLACE VIEW "public"."users_view" WITH ("security_invoker"='on') AS
 SELECT "users"."id",
    "users"."email",
    "users"."created_at"
   FROM "auth"."users";


ALTER TABLE "public"."users_view" OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_current_user_meta"() RETURNS SETOF "public"."users_view"
    LANGUAGE "sql" SECURITY DEFINER
    AS $$
  select *
  from public.users_view
  where id = auth.uid();
$$;


ALTER FUNCTION "public"."get_current_user_meta"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_tables_with_user_id"() RETURNS TABLE("table_name" "text")
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
  RETURN QUERY
  SELECT c.table_name::text
  FROM information_schema.columns c
  WHERE c.column_name = 'user_id'
  AND c.table_schema = 'public';
END;
$$;


ALTER FUNCTION "public"."get_tables_with_user_id"() OWNER TO "postgres";


SET default_tablespace = '';


SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."providers" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" character varying(255) NOT NULL,
    "description" "text" NOT NULL,
    "logo_url" "text" NOT NULL,
    "created_at" bigint NOT NULL,
    "provider_tag" "text",
    "auth_method" "text",
    "has_index_capability" boolean,
    "scopes" "jsonb",
    "is_enabled" boolean,
    "ui_component" "jsonb",
    "input_schema" "jsonb",
    "output_schema" "jsonb",
    "example_schema" "jsonb",
    "categories" "text",
    "auth_schema" "jsonb"[],
    "is_rentable" boolean
);


ALTER TABLE "public"."providers" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users_providers" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid" DEFAULT "gen_random_uuid"(),
    "provider_id" "uuid" DEFAULT "gen_random_uuid"()
);


ALTER TABLE "public"."users_providers" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."top_connected_providers" WITH ("security_invoker"='on') AS
 SELECT "p"."id" AS "provider_id",
    "p"."name",
    "p"."provider_tag",
    "count"(DISTINCT "up"."user_id") AS "count_of_users"
   FROM ("public"."users_providers" "up"
     JOIN "public"."providers" "p" ON (("up"."provider_id" = "p"."id")))
  GROUP BY "p"."id", "p"."name", "p"."provider_tag"
  ORDER BY ("count"(DISTINCT "up"."user_id")) DESC;


ALTER TABLE "public"."top_connected_providers" OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_top_connected_providers"() RETURNS SETOF "public"."top_connected_providers"
    LANGUAGE "sql" SECURITY DEFINER
    AS $$
  SELECT * FROM top_connected_providers;
$$;


ALTER FUNCTION "public"."get_top_connected_providers"() OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users_stripe" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid",
    "stripe_customer_id" "text"
);


ALTER TABLE "public"."users_stripe" OWNER TO "postgres";


-- users_subscription_status_view reads Stripe data from the "stripe" schema. In production this schema
-- holds foreign tables from the Supabase Stripe Wrapper (https://supabase.com/docs/guides/database/extensions/wrappers/stripe).
-- These empty stand-ins keep the schema working without Stripe; drop them before creating the foreign tables.
CREATE SCHEMA IF NOT EXISTS "stripe";
CREATE TABLE IF NOT EXISTS "stripe"."products" ("id" "text", "name" "text", "active" boolean, "default_price" "text", "description" "text", "created" timestamp without time zone, "updated" timestamp without time zone, "attrs" "jsonb");
CREATE TABLE IF NOT EXISTS "stripe"."prices" ("id" "text", "active" boolean, "currency" "text", "product" "text", "unit_amount" bigint, "type" "text", "created" timestamp without time zone, "attrs" "jsonb");
CREATE TABLE IF NOT EXISTS "stripe"."subscriptions" ("id" "text", "customer" "text", "currency" "text", "current_period_start" timestamp without time zone, "current_period_end" timestamp without time zone, "attrs" "jsonb");


CREATE OR REPLACE VIEW "public"."users_subscription_status_view" WITH ("security_invoker"='on') AS
 SELECT DISTINCT ON ("us"."user_id") "us"."user_id",
    "us"."stripe_customer_id",
    "s"."id" AS "subscription_id",
    ("s"."attrs" ->> 'status'::"text") AS "subscription_status",
    ("to_timestamp"(((("s"."attrs" ->> 'start_date'::"text"))::bigint)::double precision) AT TIME ZONE 'UTC'::"text") AS "subscription_start_date",
    ("to_timestamp"((((((("s"."attrs" -> 'items'::"text") -> 'data'::"text") -> 0) ->> 'current_period_end'::"text"))::bigint)::double precision) AT TIME ZONE 'UTC'::"text") AS "subscription_end_date",
    ("pr"."attrs" ->> 'lookup_key'::"text") AS "price_lookup_key",
    ((("pr"."attrs" ->> 'unit_amount'::"text"))::integer / 100) AS "amount_usd",
    "p"."name" AS "product_name",
    "p"."id" AS "product_id",
    (("s"."attrs" ->> 'cancel_at_period_end'::"text"))::boolean AS "is_canceled",
    ("to_timestamp"(((("s"."attrs" ->> 'canceled_at'::"text"))::bigint)::double precision) AT TIME ZONE 'UTC'::"text") AS "canceled_at",
    (("s"."attrs" -> 'cancellation_details'::"text") ->> 'reason'::"text") AS "cancel_reason"
   FROM ((("public"."users_stripe" "us"
     JOIN "stripe"."subscriptions" "s" ON (("s"."customer" = "us"."stripe_customer_id")))
     LEFT JOIN "stripe"."prices" "pr" ON (("pr"."id" = ((((("s"."attrs" -> 'items'::"text") -> 'data'::"text") -> 0) -> 'price'::"text") ->> 'id'::"text"))))
     LEFT JOIN "stripe"."products" "p" ON (("p"."id" = "pr"."product")))
  ORDER BY "us"."user_id", (("s"."attrs" ->> 'cancel_at_period_end'::"text"))::boolean, ("to_timestamp"(((("s"."attrs" ->> 'start_date'::"text"))::bigint)::double precision)) DESC;


ALTER TABLE "public"."users_subscription_status_view" OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_user_subscription"() RETURNS SETOF "public"."users_subscription_status_view"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
  RETURN QUERY SELECT * FROM public.get_user_subscription(auth.uid());
END;
$$;


ALTER FUNCTION "public"."get_user_subscription"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_user_subscription"("user_id" "uuid") RETURNS SETOF "public"."users_subscription_status_view"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $_$
BEGIN
  -- Проверяем, что запрашивающий пользователь запрашивает только свои данные
  IF $1 = auth.uid() THEN
    RETURN QUERY 
    SELECT * 
    FROM public.users_subscription_status_view view
    WHERE view.user_id = $1;  -- Указываем явно, что user_id берем из представления
  ELSE
    -- Если пользователь пытается получить чужие данные, возвращаем пустой результат
    RETURN;
  END IF;
END;
$_$;


ALTER FUNCTION "public"."get_user_subscription"("user_id" "uuid") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_user_tools_secure"("user_id_param" "uuid") RETURNS TABLE("tool_name" "text")
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$BEGIN
    RETURN QUERY
    SELECT uat.tool_name
    FROM public.user_available_tools uat
    WHERE uat.user_id = user_id_param
    AND uat.tool_available = true;
END;$$;


ALTER FUNCTION "public"."get_user_tools_secure"("user_id_param" "uuid") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."insert_provider_actions_for_all_users"("provider" "uuid") RETURNS "void"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    uid UUID;
BEGIN
    FOR uid IN
        SELECT user_id FROM users_providers WHERE provider_id = provider
    LOOP
        -- Insert actions for this user based on scopes
        WITH scopes_raw AS (
            SELECT scopes
            FROM users_oauth_tokens
            WHERE provider_id = provider AND user_id = uid
        ),
        scopes_array AS (
            SELECT regexp_split_to_table(replace(scopes, ' ', ','), ',') AS scope
            FROM scopes_raw
        ),
        scoped_actions AS (
            SELECT id
            FROM provider_scopes
            WHERE provider_id = provider
              AND scope_id IN (SELECT scope FROM scopes_array)
        ),
        actions_to_insert AS (
            SELECT DISTINCT pas.action_id
            FROM provider_action_scopes pas
            WHERE pas.scope_id IN (SELECT id FROM scoped_actions)
        )
        INSERT INTO users_provider_actions (user_id, action_id)
        SELECT uid, action_id
        FROM actions_to_insert
        ON CONFLICT (user_id, action_id) DO NOTHING;
    END LOOP;
END;
$$;


ALTER FUNCTION "public"."insert_provider_actions_for_all_users"("provider" "uuid") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."strip_html_tags"("text_with_tags" "text") RETURNS "text"
    LANGUAGE "sql" IMMUTABLE
    AS $$
  SELECT regexp_replace(text_with_tags, '<[^>]*>', '', 'g');
$$;


ALTER FUNCTION "public"."strip_html_tags"("text_with_tags" "text") OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."api_calls" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid",
    "endpoint" "text",
    "success" boolean,
    "error_message" "text",
    "metadata" "jsonb"
);


ALTER TABLE "public"."api_calls" OWNER TO "postgres";


ALTER TABLE "public"."api_calls" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."api_calls_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."chat_messsages_metadata" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "message_id" bigint,
    "metadata" "json"
);


ALTER TABLE "public"."chat_messsages_metadata" OWNER TO "postgres";


ALTER TABLE "public"."chat_messsages_metadata" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."chat_messsages_metadata_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."chats_chats" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone,
    "user_id" "uuid" DEFAULT "gen_random_uuid"(),
    "name" "text",
    "is_shared" boolean DEFAULT false
);


ALTER TABLE "public"."chats_chats" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."chats_messages" (
    "id" bigint NOT NULL,
    "message_id" "text",
    "chat_id" "uuid" DEFAULT "gen_random_uuid"(),
    "sender" "text",
    "image_url" "text",
    "message_text" "text",
    "is_accurate" boolean,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone,
    "metadata" "jsonb",
    "parts" "jsonb"
);


ALTER TABLE "public"."chats_messages" OWNER TO "postgres";


ALTER TABLE "public"."chats_messages" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."chats_messages_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."contact_us_requests" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "email" "text",
    "reason" "text"
);


ALTER TABLE "public"."contact_us_requests" OWNER TO "postgres";


ALTER TABLE "public"."contact_us_requests" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."contact_us_requests_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."deploy_waitlist" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid",
    "reason" "text",
    "deploy_type" "text"
);


ALTER TABLE "public"."deploy_waitlist" OWNER TO "postgres";


ALTER TABLE "public"."deploy_waitlist" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."deploy_waitlist_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."external_mcp_repositories" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text",
    "metadata" "jsonb"
);


ALTER TABLE "public"."external_mcp_repositories" OWNER TO "postgres";


ALTER TABLE "public"."external_mcp_repositories" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."external_mcp_repositories_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."flow_actions" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "flow_id" "uuid",
    "action_id" bigint
);


ALTER TABLE "public"."flow_actions" OWNER TO "postgres";


ALTER TABLE "public"."flow_actions" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."flow_actions_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."user_flow_runs" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "flow_id" "uuid",
    "run_status" "text",
    "payload" "jsonb",
    "run_at" "text",
    "completed_at" "text",
    "run_id" "uuid" DEFAULT "gen_random_uuid"(),
    "user_input" "text"
);


ALTER TABLE "public"."user_flow_runs" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."flow_runs_view" WITH ("security_invoker"='on') AS
 SELECT "user_flow_runs"."run_id",
    "user_flow_runs"."flow_id",
    "user_flow_runs"."run_status",
    "user_flow_runs"."payload",
    "user_flow_runs"."run_at",
    "user_flow_runs"."completed_at"
   FROM "public"."user_flow_runs";


ALTER TABLE "public"."flow_runs_view" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."flows_messages" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "flow_id" "uuid",
    "sender" "text",
    "type" "text",
    "message_text" "text",
    "metadata" "text",
    "parts" "text",
    "user_id" "uuid",
    "message_id" "text"
);


ALTER TABLE "public"."flows_messages" OWNER TO "postgres";


ALTER TABLE "public"."flows_messages" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."flows_messages_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."integration_requests" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid",
    "integration_name" "text"
);


ALTER TABLE "public"."integration_requests" OWNER TO "postgres";


ALTER TABLE "public"."integration_requests" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."integration_request_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."jobs_export_batches" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "job_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "status" "text",
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    "item_count" integer DEFAULT 0,
    "processed_count" integer DEFAULT 0,
    "error" "text",
    "batch_number" integer DEFAULT 0,
    "retry_payload" "jsonb"
);


ALTER TABLE "public"."jobs_export_batches" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."mcp_repositories" (
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "image_name" character varying,
    "repo_url" "text",
    "env" "jsonb",
    "docker_file_b64" "text",
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "last_commit_hash" "text",
    "name" "text",
    "description" "text",
    "input_schema" "jsonb",
    "author_user_id" "uuid",
    "is_approved" boolean,
    "metadata" "jsonb"
);


ALTER TABLE "public"."mcp_repositories" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."mcp_repository_deployments" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "repo_id" "uuid",
    "build_logs" "jsonb",
    "status" "text",
    "error" "text",
    "commit_hash" "text",
    "deployment_id" "uuid" DEFAULT "gen_random_uuid"()
);


ALTER TABLE "public"."mcp_repository_deployments" OWNER TO "postgres";


ALTER TABLE "public"."mcp_repository_deployments" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."mcp_repository_deployments_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."omi_users" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid",
    "omi_user_id" "text"
);


ALTER TABLE "public"."omi_users" OWNER TO "postgres";


ALTER TABLE "public"."omi_users" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."omi_users_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE OR REPLACE VIEW "public"."popular_providers_view" WITH ("security_invoker"='on') AS
 SELECT "up"."provider_id",
    "count"(*) AS "usage_count"
   FROM ("public"."users_providers" "up"
     JOIN "public"."providers" "p" ON (("up"."provider_id" = "p"."id")))
  WHERE ("p"."is_enabled" = true)
  GROUP BY "up"."provider_id"
  ORDER BY ("count"(*)) DESC
 LIMIT 10;


ALTER TABLE "public"."popular_providers_view" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."products_info" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "product_tag" "text" DEFAULT ''::"text",
    "attrs" "jsonb",
    "name" "text",
    "stripe_product_id" "text"
);


ALTER TABLE "public"."products_info" OWNER TO "postgres";


ALTER TABLE "public"."products_info" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."products_info_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."provider_action_scopes" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "action_id" bigint,
    "scope_id" bigint
);


ALTER TABLE "public"."provider_action_scopes" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."provider_scopes" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "scope_name" "text",
    "scope_id" "text",
    "provider_id" "uuid" DEFAULT "gen_random_uuid"()
);


ALTER TABLE "public"."provider_scopes" OWNER TO "postgres";


ALTER TABLE "public"."provider_scopes" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."provider_action_scopes_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


ALTER TABLE "public"."provider_action_scopes" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."provider_action_scopes_id_seq1"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."provider_actions" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "action_name" "text",
    "action_slug" "text",
    "input_schema" "jsonb",
    "output_schema" "jsonb",
    "examples" "jsonb",
    "provider_id" "uuid",
    "ui_component" "jsonb"
);


ALTER TABLE "public"."provider_actions" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."provider_actions_with_scopes_view" WITH ("security_invoker"='on') AS
 SELECT "p"."name" AS "provider_name",
    "pa"."id" AS "action_id",
    "pa"."action_name",
    "pa"."action_slug",
    "array_agg"(DISTINCT "ps"."scope_id") AS "scope_ids",
    "array_agg"(DISTINCT "ps"."scope_name") AS "scope_names"
   FROM ((("public"."providers" "p"
     JOIN "public"."provider_actions" "pa" ON (("pa"."provider_id" = "p"."id")))
     LEFT JOIN "public"."provider_action_scopes" "pas" ON (("pas"."action_id" = "pa"."id")))
     LEFT JOIN "public"."provider_scopes" "ps" ON (("ps"."id" = "pas"."scope_id")))
  GROUP BY "p"."name", "pa"."id", "pa"."action_name", "pa"."action_slug"
  ORDER BY "p"."name", "pa"."action_name";


ALTER TABLE "public"."provider_actions_with_scopes_view" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."provider_tools" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "provider_id" "uuid" DEFAULT "gen_random_uuid"(),
    "tool_name" "text",
    "require_scope" boolean,
    "require_index" boolean,
    "scopes" "text"
);


ALTER TABLE "public"."provider_tools" OWNER TO "postgres";


ALTER TABLE "public"."provider_tools" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."provider_tools_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


ALTER TABLE "public"."provider_actions" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."providers_actions_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."rent_api_keys" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "provider_id" "uuid",
    "api_key" "text"
);


ALTER TABLE "public"."rent_api_keys" OWNER TO "postgres";


ALTER TABLE "public"."rent_api_keys" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."rent_api_keys_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."user_flows" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text",
    "description" "text",
    "status" "text",
    "user_id" "uuid",
    "is_shared" boolean,
    "plain_description" "text",
    "is_template" boolean
);


ALTER TABLE "public"."user_flows" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."user_actions_flows_view" WITH ("security_invoker"='on') AS
 SELECT "uf"."user_id",
    "uf"."id" AS "flow_id",
    "uf"."name" AS "flow_name",
    "uf"."description" AS "flow_description",
    "uf"."plain_description" AS "flow_plain_description",
    "fa"."action_id",
    "pa"."id" AS "provider_action_id",
    "pa"."action_name",
    "pa"."action_slug",
    "pa"."input_schema",
    "pa"."output_schema",
    "pa"."provider_id",
    "p"."name" AS "provider_name",
    "p"."provider_tag" AS "provider_slug"
   FROM ((("public"."user_flows" "uf"
     JOIN "public"."flow_actions" "fa" ON (("uf"."id" = "fa"."flow_id")))
     JOIN "public"."provider_actions" "pa" ON (("fa"."action_id" = "pa"."id")))
     JOIN "public"."providers" "p" ON (("pa"."provider_id" = "p"."id")));


ALTER TABLE "public"."user_actions_flows_view" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users_provider_actions" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid" NOT NULL,
    "action_id" bigint NOT NULL
);


ALTER TABLE "public"."users_provider_actions" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."user_actions_view" WITH ("security_invoker"='on') AS
 SELECT "p"."id" AS "provider_id",
    "p"."name" AS "provider_name",
    "p"."provider_tag",
    "p"."logo_url",
    "pa"."action_name",
    "pa"."action_slug",
    "pa"."input_schema",
    "pa"."examples",
    "pa"."id" AS "action_id",
    "upa"."user_id"
   FROM (("public"."users_provider_actions" "upa"
     JOIN "public"."provider_actions" "pa" ON (("pa"."id" = "upa"."action_id")))
     JOIN "public"."providers" "p" ON (("p"."id" = "pa"."provider_id")));


ALTER TABLE "public"."user_actions_view" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_auth_codes" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "code" "uuid" DEFAULT "gen_random_uuid"(),
    "user_id" "uuid",
    "provider_id" "uuid",
    "used" boolean,
    "expires_at" timestamp with time zone,
    "used_at" timestamp with time zone,
    "encrypted_api_key" "text",
    "repo_id" "uuid",
    "type" "text"
);


ALTER TABLE "public"."user_auth_codes" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users_oauth_tokens" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "user_id" "uuid" NOT NULL,
    "provider_id" "uuid" NOT NULL,
    "access_token" character varying NOT NULL,
    "refresh_token" character varying,
    "expires_at" bigint,
    "scopes" "text" NOT NULL,
    "raw_token_data" "json",
    "created_at" timestamp without time zone DEFAULT "now"()
);


ALTER TABLE "public"."users_oauth_tokens" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users_provider_indexes" (
    "id" bigint NOT NULL,
    "provider_id" "uuid" DEFAULT "gen_random_uuid"(),
    "user_id" "uuid" DEFAULT "gen_random_uuid"(),
    "collection_name" character varying,
    "status" character varying,
    "last_sync_date" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "processed_entities" bigint
);


ALTER TABLE "public"."users_provider_indexes" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."user_available_tools" WITH ("security_invoker"='on') AS
 SELECT "u"."id" AS "user_id",
    "pt"."id" AS "tool_id",
    "pt"."tool_name",
        CASE
            WHEN (NOT (EXISTS ( SELECT 1
               FROM "public"."users_providers" "up_1"
              WHERE (("up_1"."user_id" = "u"."id") AND ("up_1"."provider_id" = "p"."id"))))) THEN false
            WHEN (("pt"."require_scope" = false) AND ("pt"."require_index" = false)) THEN true
            WHEN (("pt"."require_scope" = true) AND (EXISTS ( SELECT 1
               FROM "unnest"("string_to_array"("pt"."scopes", ','::"text")) "required_scope"("required_scope")
              WHERE (TRIM(BOTH FROM "required_scope"."required_scope") IN ( SELECT TRIM(BOTH FROM "user_scope"."user_scope") AS "btrim"
                       FROM "unnest"("string_to_array"("uot"."scopes", ','::"text")) "user_scope"("user_scope")))))) THEN true
            WHEN (("pt"."require_index" = true) AND (EXISTS ( SELECT 1
               FROM "public"."users_provider_indexes" "upi"
              WHERE (("upi"."user_id" = "u"."id") AND ("upi"."provider_id" = "p"."id") AND (("upi"."status")::"text" = 'synced'::"text"))))) THEN true
            ELSE false
        END AS "tool_available"
   FROM (((("auth"."users" "u"
     JOIN "public"."users_providers" "up" ON (("u"."id" = "up"."user_id")))
     JOIN "public"."providers" "p" ON (("up"."provider_id" = "p"."id")))
     JOIN "public"."provider_tools" "pt" ON (("p"."id" = "pt"."provider_id")))
     LEFT JOIN "public"."users_oauth_tokens" "uot" ON ((("u"."id" = "uot"."user_id") AND ("uot"."provider_id" = "p"."id"))))
  ORDER BY "u"."id", "pt"."tool_name";


ALTER TABLE "public"."user_available_tools" OWNER TO "postgres";


ALTER TABLE "public"."user_flow_runs" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."user_flow_runs_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."user_flow_schedules" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "flow_id" "uuid",
    "schedule" "jsonb",
    "qstash_schedule_id" "text"
);


ALTER TABLE "public"."user_flow_schedules" OWNER TO "postgres";


ALTER TABLE "public"."user_flow_schedules" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."user_flow_schedules_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE OR REPLACE VIEW "public"."user_monthly_usage_view" WITH ("security_invoker"='on') AS
 SELECT "u"."user_id",
    ( SELECT "count"(*) AS "count"
           FROM "public"."api_calls" "ac"
          WHERE (("ac"."user_id" = "u"."user_id") AND ("ac"."created_at" >= "date_trunc"('month'::"text", (CURRENT_DATE)::timestamp with time zone)) AND ("ac"."created_at" < ("date_trunc"('month'::"text", (CURRENT_DATE)::timestamp with time zone) + '1 mon'::interval)))) AS "api_call_count",
    ( SELECT "count"(*) AS "count"
           FROM "public"."chats_chats" "cc"
          WHERE (("cc"."user_id" = "u"."user_id") AND ("cc"."created_at" >= "date_trunc"('month'::"text", (CURRENT_DATE)::timestamp with time zone)) AND ("cc"."created_at" < ("date_trunc"('month'::"text", (CURRENT_DATE)::timestamp with time zone) + '1 mon'::interval)))) AS "chat_count",
    ( SELECT "count"(*) AS "count"
           FROM "public"."user_flows" "uf"
          WHERE (("uf"."user_id" = "u"."user_id") AND ("uf"."status" = 'Active'::"text"))) AS "active_flow_count",
    ( SELECT "count"(*) AS "count"
           FROM ( SELECT "cm"."id"
                   FROM ("public"."chats_messages" "cm"
                     JOIN "public"."chats_chats" "cc" ON (("cm"."chat_id" = "cc"."id")))
                  WHERE (("cc"."user_id" = "u"."user_id") AND ("cm"."sender" = 'assistant'::"text") AND ("cm"."created_at" >= "date_trunc"('month'::"text", (CURRENT_DATE)::timestamp with time zone)) AND ("cm"."created_at" < ("date_trunc"('month'::"text", (CURRENT_DATE)::timestamp with time zone) + '1 mon'::interval)))
                UNION ALL
                 SELECT "fm"."id"
                   FROM "public"."flows_messages" "fm"
                  WHERE (("fm"."user_id" = "u"."user_id") AND ("fm"."sender" = 'assistant'::"text") AND ("fm"."created_at" >= "date_trunc"('month'::"text", (CURRENT_DATE)::timestamp with time zone)) AND ("fm"."created_at" < ("date_trunc"('month'::"text", (CURRENT_DATE)::timestamp with time zone) + '1 mon'::interval)))) "all_messages") AS "message_count"
   FROM ( SELECT "api_calls"."user_id"
           FROM "public"."api_calls"
        UNION
         SELECT "chats_chats"."user_id"
           FROM "public"."chats_chats"
        UNION
         SELECT "user_flows"."user_id"
           FROM "public"."user_flows"
        UNION
         SELECT "flows_messages"."user_id"
           FROM "public"."flows_messages") "u";


ALTER TABLE "public"."user_monthly_usage_view" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_playground_settings" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "agent_prompt" "text",
    "ai_model" "text",
    "user_id" "uuid",
    "api_key_provider_name" "text",
    "api_key" "text",
    "api_key_enabled" boolean
);


ALTER TABLE "public"."user_playground_settings" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_provider_custom_auth" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid" DEFAULT "gen_random_uuid"(),
    "provider_id" "uuid" DEFAULT "gen_random_uuid"(),
    "raw_data" "jsonb"
);


ALTER TABLE "public"."user_provider_custom_auth" OWNER TO "postgres";


COMMENT ON TABLE "public"."user_provider_custom_auth" IS 'Data for custom auth';


ALTER TABLE "public"."user_provider_custom_auth" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."user_provider_custom_auth_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE OR REPLACE VIEW "public"."user_provider_scopes_view" WITH ("security_invoker"='on') AS
 SELECT "upa"."user_id",
    "p"."id" AS "provider_id",
    "array_agg"(DISTINCT "ps"."scope_id") AS "scope_ids",
    "array_agg"(DISTINCT "ps"."scope_name") AS "scope_names"
   FROM (((("public"."users_provider_actions" "upa"
     JOIN "public"."provider_actions" "pa" ON (("pa"."id" = "upa"."action_id")))
     JOIN "public"."providers" "p" ON (("p"."id" = "pa"."provider_id")))
     JOIN "public"."provider_action_scopes" "pas" ON (("pas"."action_id" = "pa"."id")))
     JOIN "public"."provider_scopes" "ps" ON (("ps"."id" = "pas"."scope_id")))
  GROUP BY "upa"."user_id", "p"."id"
  ORDER BY "upa"."user_id", "p"."id";


ALTER TABLE "public"."user_provider_scopes_view" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_tools_experimental" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid" DEFAULT "gen_random_uuid"(),
    "tools" "jsonb"
);


ALTER TABLE "public"."user_tools_experimental" OWNER TO "postgres";


ALTER TABLE "public"."user_tools_experimental" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."user_tools_experimental_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_api_keys" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "api_key" "text" DEFAULT ''::"text",
    "user_id" "uuid" DEFAULT "gen_random_uuid"()
);


ALTER TABLE "public"."users_api_keys" OWNER TO "postgres";


ALTER TABLE "public"."users_api_keys" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_api_keys_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_beta" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "email" "text",
    "social_url" "text"
);


ALTER TABLE "public"."users_beta" OWNER TO "postgres";


ALTER TABLE "public"."users_beta" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_beta_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_data_export" (
    "id" "text" NOT NULL,
    "user_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "provider_id" "uuid",
    "type" "text",
    "source" "text",
    "input_hash" "text",
    "input_params" "jsonb",
    "raw_response" "jsonb",
    "title" "text",
    "full_index" "text",
    "created_at" timestamp with time zone,
    "job_id" "uuid" DEFAULT "gen_random_uuid"()
);


ALTER TABLE "public"."users_data_export" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users_db_access" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "provider_id" "uuid" DEFAULT "gen_random_uuid"(),
    "user_id" "uuid" DEFAULT "gen_random_uuid"(),
    "credentials" "jsonb"
);


ALTER TABLE "public"."users_db_access" OWNER TO "postgres";


ALTER TABLE "public"."users_db_access" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_db_acess_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_export_jobs" (
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid" DEFAULT "gen_random_uuid"(),
    "exporter" "text",
    "status" "text",
    "updated_at" timestamp without time zone DEFAULT "now"(),
    "total_items" integer DEFAULT 0,
    "error" "text",
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "params" "jsonb" DEFAULT 'null'::"jsonb",
    "last_batch" integer DEFAULT 0,
    "sink" "text"
);


ALTER TABLE "public"."users_export_jobs" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users_feedback" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid" DEFAULT "gen_random_uuid"(),
    "text" "text",
    "mood" "text"
);


ALTER TABLE "public"."users_feedback" OWNER TO "postgres";


ALTER TABLE "public"."users_feedback" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_feedback_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_mcp" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid",
    "repo_id" "uuid",
    "env" "jsonb",
    "status" "text",
    "error" "text",
    "process_id" "text"
);


ALTER TABLE "public"."users_mcp" OWNER TO "postgres";


ALTER TABLE "public"."users_mcp" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_mcp_repository_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_memory" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "memory" "text",
    "tool" "text",
    "user_id" "uuid" DEFAULT "gen_random_uuid"()
);


ALTER TABLE "public"."users_memory" OWNER TO "postgres";


ALTER TABLE "public"."users_memory" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_memory_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


ALTER TABLE "public"."users_provider_actions" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_provider_actions_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_provider_api_keys" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "api_key" "text",
    "user_id" "uuid" DEFAULT "gen_random_uuid"(),
    "provider_id" "uuid" DEFAULT "gen_random_uuid"(),
    "raw_data" "jsonb"
);


ALTER TABLE "public"."users_provider_api_keys" OWNER TO "postgres";


ALTER TABLE "public"."users_provider_api_keys" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_provider_api_keys_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


ALTER TABLE "public"."users_provider_indexes" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_provider_indexes_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_provider_rent_api_keys" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid",
    "rent_key_id" bigint
);


ALTER TABLE "public"."users_provider_rent_api_keys" OWNER TO "postgres";


ALTER TABLE "public"."users_provider_rent_api_keys" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_provider_rent_api_keys_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


ALTER TABLE "public"."users_providers" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_providers_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


ALTER TABLE "public"."users_stripe" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_stripe_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_team_requests" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "email" "text",
    "company" "text"
);


ALTER TABLE "public"."users_team_requests" OWNER TO "postgres";


ALTER TABLE "public"."users_team_requests" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_team_requests_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE IF NOT EXISTS "public"."users_waitlist" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "email" "text"
);


ALTER TABLE ONLY "public"."users_waitlist" FORCE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_waitlist" OWNER TO "postgres";


ALTER TABLE "public"."users_waitlist" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_waitlist_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


ALTER TABLE ONLY "public"."api_calls"
    ADD CONSTRAINT "api_calls_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."chat_messsages_metadata"
    ADD CONSTRAINT "chat_messsages_metadata_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."chats_chats"
    ADD CONSTRAINT "chats_chats_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."chats_messages"
    ADD CONSTRAINT "chats_messages_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."contact_us_requests"
    ADD CONSTRAINT "contact_us_requests_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."deploy_waitlist"
    ADD CONSTRAINT "deploy_waitlist_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."external_mcp_repositories"
    ADD CONSTRAINT "external_mcp_repositories_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."flow_actions"
    ADD CONSTRAINT "flow_actions_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."flows_messages"
    ADD CONSTRAINT "flows_messages_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."integration_requests"
    ADD CONSTRAINT "integration_request_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."jobs_export_batches"
    ADD CONSTRAINT "jobs_export_batches_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."mcp_repositories"
    ADD CONSTRAINT "mcp_repositories_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."mcp_repository_deployments"
    ADD CONSTRAINT "mcp_repository_deployments_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."omi_users"
    ADD CONSTRAINT "omi_users_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."user_playground_settings"
    ADD CONSTRAINT "playground_settings_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."products_info"
    ADD CONSTRAINT "products_info_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."provider_scopes"
    ADD CONSTRAINT "provider_action_scopes_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."provider_action_scopes"
    ADD CONSTRAINT "provider_action_scopes_pkey1" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."providers"
    ADD CONSTRAINT "provider_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."providers"
    ADD CONSTRAINT "provider_provider_tag_key" UNIQUE ("provider_tag");


ALTER TABLE ONLY "public"."provider_tools"
    ADD CONSTRAINT "provider_tools_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."provider_actions"
    ADD CONSTRAINT "providers_actions_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."rent_api_keys"
    ADD CONSTRAINT "rent_api_keys_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."rent_api_keys"
    ADD CONSTRAINT "rent_api_keys_provider_id_key" UNIQUE ("provider_id");


ALTER TABLE ONLY "public"."mcp_repositories"
    ADD CONSTRAINT "unique_repo_url" UNIQUE ("repo_url");


ALTER TABLE ONLY "public"."users_provider_actions"
    ADD CONSTRAINT "unique_user_action" UNIQUE ("user_id", "action_id");


ALTER TABLE ONLY "public"."users_provider_rent_api_keys"
    ADD CONSTRAINT "unique_users_rent_api_keys" UNIQUE ("user_id", "rent_key_id");


ALTER TABLE ONLY "public"."user_flow_runs"
    ADD CONSTRAINT "user_flow_runs_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."user_flow_schedules"
    ADD CONSTRAINT "user_flow_schedules_flow_id_key" UNIQUE ("flow_id");


ALTER TABLE ONLY "public"."user_flow_schedules"
    ADD CONSTRAINT "user_flow_schedules_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."user_flows"
    ADD CONSTRAINT "user_flows_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_oauth_tokens"
    ADD CONSTRAINT "user_oauth_token_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_oauth_tokens"
    ADD CONSTRAINT "user_oauth_tokens_user_id_provider_id_key" UNIQUE ("user_id", "provider_id");


ALTER TABLE ONLY "public"."user_auth_codes"
    ADD CONSTRAINT "user_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."user_provider_custom_auth"
    ADD CONSTRAINT "user_provider_custom_auth_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."user_tools_experimental"
    ADD CONSTRAINT "user_tools_experimental_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_api_keys"
    ADD CONSTRAINT "users_api_keys_api_key_key" UNIQUE ("api_key");


ALTER TABLE ONLY "public"."users_api_keys"
    ADD CONSTRAINT "users_api_keys_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_beta"
    ADD CONSTRAINT "users_beta_email_key" UNIQUE ("email");


ALTER TABLE ONLY "public"."users_beta"
    ADD CONSTRAINT "users_beta_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_data_export"
    ADD CONSTRAINT "users_data_export_pkey" PRIMARY KEY ("id", "user_id");


ALTER TABLE ONLY "public"."users_db_access"
    ADD CONSTRAINT "users_db_acess_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_export_jobs"
    ADD CONSTRAINT "users_export_jobs_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_feedback"
    ADD CONSTRAINT "users_feedback_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_mcp"
    ADD CONSTRAINT "users_mcp_process_id_key" UNIQUE ("process_id");


ALTER TABLE ONLY "public"."users_mcp"
    ADD CONSTRAINT "users_mcp_repository_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_memory"
    ADD CONSTRAINT "users_memory_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_provider_actions"
    ADD CONSTRAINT "users_provider_actions_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_provider_api_keys"
    ADD CONSTRAINT "users_provider_api_keys_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_provider_indexes"
    ADD CONSTRAINT "users_provider_indexes_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_provider_indexes"
    ADD CONSTRAINT "users_provider_indexes_user_id_provider_id_key" UNIQUE ("user_id", "provider_id");


ALTER TABLE ONLY "public"."users_provider_rent_api_keys"
    ADD CONSTRAINT "users_provider_rent_api_keys_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_providers"
    ADD CONSTRAINT "users_providers_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_providers"
    ADD CONSTRAINT "users_providers_provider_id_user_id_key" UNIQUE ("provider_id", "user_id");


ALTER TABLE ONLY "public"."users_stripe"
    ADD CONSTRAINT "users_stripe_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_stripe"
    ADD CONSTRAINT "users_stripe_user_id_key" UNIQUE ("user_id");


ALTER TABLE ONLY "public"."users_team_requests"
    ADD CONSTRAINT "users_team_requests_pkey" PRIMARY KEY ("id");


ALTER TABLE ONLY "public"."users_waitlist"
    ADD CONSTRAINT "users_waitlist_email_key" UNIQUE ("email");


ALTER TABLE ONLY "public"."users_waitlist"
    ADD CONSTRAINT "users_waitlist_pkey" PRIMARY KEY ("id");


CREATE INDEX "idx_user_oauth_token_provider" ON "public"."users_oauth_tokens" USING "btree" ("provider_id");


CREATE INDEX "idx_user_oauth_token_user_id" ON "public"."users_oauth_tokens" USING "btree" ("user_id");


CREATE INDEX "provider_scopes_scope_id_provider_id_idx" ON "public"."provider_scopes" USING "btree" ("scope_id", "provider_id");


CREATE UNIQUE INDEX "users_mcp_user_repo_idx" ON "public"."users_mcp" USING "btree" ("user_id", "repo_id");


ALTER TABLE ONLY "public"."api_calls"
    ADD CONSTRAINT "api_calls_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."chat_messsages_metadata"
    ADD CONSTRAINT "chat_messsages_metadata_message_id_fkey" FOREIGN KEY ("message_id") REFERENCES "public"."chats_messages"("id");


ALTER TABLE ONLY "public"."chats_chats"
    ADD CONSTRAINT "chats_chats_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."chats_messages"
    ADD CONSTRAINT "chats_messages_chat_id_fkey" FOREIGN KEY ("chat_id") REFERENCES "public"."chats_chats"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."deploy_waitlist"
    ADD CONSTRAINT "deploy_waitlist_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."flow_actions"
    ADD CONSTRAINT "flow_actions_action_id_fkey" FOREIGN KEY ("action_id") REFERENCES "public"."provider_actions"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."flow_actions"
    ADD CONSTRAINT "flow_actions_flow_id_fkey" FOREIGN KEY ("flow_id") REFERENCES "public"."user_flows"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."flows_messages"
    ADD CONSTRAINT "flows_messages_flow_id_fkey" FOREIGN KEY ("flow_id") REFERENCES "public"."user_flows"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."flows_messages"
    ADD CONSTRAINT "flows_messages_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."integration_requests"
    ADD CONSTRAINT "integration_request_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."jobs_export_batches"
    ADD CONSTRAINT "jobs_export_batches_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "public"."users_export_jobs"("id");


ALTER TABLE ONLY "public"."mcp_repositories"
    ADD CONSTRAINT "mcp_repositories_author_user_id_fkey" FOREIGN KEY ("author_user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."mcp_repository_deployments"
    ADD CONSTRAINT "mcp_repository_deployments_repo_id_fkey" FOREIGN KEY ("repo_id") REFERENCES "public"."mcp_repositories"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."omi_users"
    ADD CONSTRAINT "omi_users_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."user_playground_settings"
    ADD CONSTRAINT "playground_settings_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."provider_action_scopes"
    ADD CONSTRAINT "provider_action_scopes_action_id_fkey" FOREIGN KEY ("action_id") REFERENCES "public"."provider_actions"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."provider_action_scopes"
    ADD CONSTRAINT "provider_action_scopes_scope_id_fkey" FOREIGN KEY ("scope_id") REFERENCES "public"."provider_scopes"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."provider_actions"
    ADD CONSTRAINT "provider_actions_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."provider_scopes"
    ADD CONSTRAINT "provider_scopes_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."provider_tools"
    ADD CONSTRAINT "provider_tools_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."rent_api_keys"
    ADD CONSTRAINT "rent_api_keys_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id");


ALTER TABLE ONLY "public"."user_auth_codes"
    ADD CONSTRAINT "user_auth_codes_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."user_auth_codes"
    ADD CONSTRAINT "user_auth_codes_repo_id_fkey" FOREIGN KEY ("repo_id") REFERENCES "public"."mcp_repositories"("id");


ALTER TABLE ONLY "public"."user_flow_runs"
    ADD CONSTRAINT "user_flow_runs_flow_id_fkey" FOREIGN KEY ("flow_id") REFERENCES "public"."user_flows"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."user_flow_schedules"
    ADD CONSTRAINT "user_flow_schedules_flow_id_fkey" FOREIGN KEY ("flow_id") REFERENCES "public"."user_flows"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."user_flows"
    ADD CONSTRAINT "user_flows_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_oauth_tokens"
    ADD CONSTRAINT "user_oauth_token_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."user_provider_custom_auth"
    ADD CONSTRAINT "user_provider_custom_auth_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."user_provider_custom_auth"
    ADD CONSTRAINT "user_provider_custom_auth_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."user_tools_experimental"
    ADD CONSTRAINT "user_tools_experimental_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."user_auth_codes"
    ADD CONSTRAINT "user_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."users_api_keys"
    ADD CONSTRAINT "users_api_keys_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."users_data_export"
    ADD CONSTRAINT "users_data_export_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "public"."users_export_jobs"("id");


ALTER TABLE ONLY "public"."users_data_export"
    ADD CONSTRAINT "users_data_export_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."users_db_access"
    ADD CONSTRAINT "users_db_access_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_db_access"
    ADD CONSTRAINT "users_db_acess_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id");


ALTER TABLE ONLY "public"."users_export_jobs"
    ADD CONSTRAINT "users_export_jobs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."users_feedback"
    ADD CONSTRAINT "users_feedback_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_mcp"
    ADD CONSTRAINT "users_mcp_repo_id_fkey" FOREIGN KEY ("repo_id") REFERENCES "public"."mcp_repositories"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_mcp"
    ADD CONSTRAINT "users_mcp_repository_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."users_memory"
    ADD CONSTRAINT "users_memory_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_oauth_tokens"
    ADD CONSTRAINT "users_oauth_tokens_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_provider_actions"
    ADD CONSTRAINT "users_provider_actions_action_id_fkey" FOREIGN KEY ("action_id") REFERENCES "public"."provider_actions"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_provider_actions"
    ADD CONSTRAINT "users_provider_actions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_provider_api_keys"
    ADD CONSTRAINT "users_provider_api_keys_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id");


ALTER TABLE ONLY "public"."users_provider_api_keys"
    ADD CONSTRAINT "users_provider_api_keys_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_provider_indexes"
    ADD CONSTRAINT "users_provider_indexes_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id");


ALTER TABLE ONLY "public"."users_provider_indexes"
    ADD CONSTRAINT "users_provider_indexes_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


ALTER TABLE ONLY "public"."users_provider_rent_api_keys"
    ADD CONSTRAINT "users_provider_rent_api_keys_rent_key_id_fkey" FOREIGN KEY ("rent_key_id") REFERENCES "public"."rent_api_keys"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_provider_rent_api_keys"
    ADD CONSTRAINT "users_provider_rent_api_keys_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_providers"
    ADD CONSTRAINT "users_providers_provider_id_fkey" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_providers"
    ADD CONSTRAINT "users_providers_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


ALTER TABLE ONLY "public"."users_stripe"
    ADD CONSTRAINT "users_stripe_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");


CREATE POLICY "Allow access to own runs via user_flows" ON "public"."user_flow_runs" USING ((EXISTS ( SELECT 1
   FROM "public"."user_flows"
  WHERE (("user_flows"."id" = "user_flow_runs"."flow_id") AND ("user_flows"."user_id" = "auth"."uid"()))))) WITH CHECK ((EXISTS ( SELECT 1
   FROM "public"."user_flows"
  WHERE (("user_flows"."id" = "user_flow_runs"."flow_id") AND ("user_flows"."user_id" = "auth"."uid"())))));


CREATE POLICY "Allow access to own schedules via user_flows" ON "public"."user_flow_schedules" USING ((EXISTS ( SELECT 1
   FROM "public"."user_flows"
  WHERE (("user_flows"."id" = "user_flow_schedules"."flow_id") AND ("user_flows"."user_id" = "auth"."uid"()))))) WITH CHECK ((EXISTS ( SELECT 1
   FROM "public"."user_flows"
  WHERE (("user_flows"."id" = "user_flow_schedules"."flow_id") AND ("user_flows"."user_id" = "auth"."uid"())))));


CREATE POLICY "Allow admin delete access" ON "public"."deploy_waitlist" FOR DELETE TO "service_role" USING (true);


CREATE POLICY "Allow admin select access" ON "public"."deploy_waitlist" FOR SELECT TO "service_role" USING (true);


CREATE POLICY "Allow admin update access" ON "public"."deploy_waitlist" FOR UPDATE TO "service_role" USING (true);


CREATE POLICY "Allow anyone to insert" ON "public"."users_beta" FOR INSERT WITH CHECK (true);


CREATE POLICY "Allow authenticated insert access" ON "public"."deploy_waitlist" FOR INSERT TO "authenticated" WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Allow authors to insert into their repositories" ON "public"."mcp_repository_deployments" FOR INSERT WITH CHECK ((EXISTS ( SELECT 1
   FROM "public"."mcp_repositories"
  WHERE (("mcp_repositories"."id" = "mcp_repository_deployments"."repo_id") AND ("mcp_repositories"."author_user_id" = "auth"."uid"())))));


CREATE POLICY "Allow authors to read their deployments" ON "public"."mcp_repository_deployments" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM "public"."mcp_repositories"
  WHERE (("mcp_repositories"."id" = "mcp_repository_deployments"."repo_id") AND ("mcp_repositories"."author_user_id" = "auth"."uid"())))));


CREATE POLICY "Allow insert for all users" ON "public"."mcp_repositories" FOR INSERT WITH CHECK (true);


CREATE POLICY "Allow public insert access" ON "public"."contact_us_requests" FOR INSERT TO "authenticated", "anon" WITH CHECK (true);


CREATE POLICY "Allow read access to everyone" ON "public"."products_info" FOR SELECT USING (true);


CREATE POLICY "Allow select for all users" ON "public"."mcp_repositories" FOR SELECT USING (true);


CREATE POLICY "Allow update for all users" ON "public"."mcp_repositories" FOR UPDATE USING (true) WITH CHECK (true);


CREATE POLICY "Allow user to delete their own API keys" ON "public"."users_api_keys" FOR DELETE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Allow user to delete their own provider API keys" ON "public"."users_provider_api_keys" FOR DELETE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Allow user to insert their own API keys" ON "public"."users_api_keys" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Allow user to insert their own provider API keys" ON "public"."users_provider_api_keys" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Allow user to read their own API keys" ON "public"."users_api_keys" FOR SELECT USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Allow user to read their own provider API keys" ON "public"."users_provider_api_keys" FOR SELECT USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Allow user to update their own API keys" ON "public"."users_api_keys" FOR UPDATE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Allow user to update their own provider API keys" ON "public"."users_provider_api_keys" FOR UPDATE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Anyone can add a request" ON "public"."users_team_requests" FOR INSERT WITH CHECK (true);


CREATE POLICY "Enable delete for users with chat access" ON "public"."chats_messages" FOR DELETE TO "authenticated" USING ((EXISTS ( SELECT 1
   FROM "public"."chats_chats"
  WHERE (("chats_chats"."id" = "chats_messages"."chat_id") AND ("chats_chats"."user_id" = "auth"."uid"())))));


CREATE POLICY "Enable insert for authenticated users" ON "public"."chats_messages" FOR INSERT TO "authenticated" WITH CHECK ((EXISTS ( SELECT 1
   FROM "public"."chats_chats"
  WHERE (("chats_chats"."id" = "chats_messages"."chat_id") AND ("chats_chats"."user_id" = "auth"."uid"())))));


CREATE POLICY "Enable read access for all users" ON "public"."provider_action_scopes" FOR SELECT USING (true);


CREATE POLICY "Enable read access for all users" ON "public"."provider_scopes" FOR SELECT USING (true);


CREATE POLICY "Enable read access for users with chat access" ON "public"."chats_messages" FOR SELECT TO "authenticated" USING ((EXISTS ( SELECT 1
   FROM "public"."chats_chats"
  WHERE (("chats_chats"."id" = "chats_messages"."chat_id") AND ("chats_chats"."user_id" = "auth"."uid"())))));


CREATE POLICY "Enable update for users based on user_id" ON "public"."users_provider_indexes" FOR UPDATE USING ((( SELECT "auth"."uid"() AS "uid") = "user_id"));


CREATE POLICY "Enable update for users with chat access" ON "public"."chats_messages" FOR UPDATE TO "authenticated" USING ((EXISTS ( SELECT 1
   FROM "public"."chats_chats"
  WHERE (("chats_chats"."id" = "chats_messages"."chat_id") AND ("chats_chats"."user_id" = "auth"."uid"())))));


CREATE POLICY "Insert for Anyone" ON "public"."users_waitlist" FOR INSERT TO "anon" WITH CHECK (true);


CREATE POLICY "Providers are viewable by everyone" ON "public"."providers" FOR SELECT USING (true);


CREATE POLICY "Public Read Access" ON "public"."external_mcp_repositories" FOR SELECT USING (true);


CREATE POLICY "Public Read Access" ON "public"."mcp_repositories" FOR SELECT USING (true);


CREATE POLICY "User can access only their own keys" ON "public"."users_provider_rent_api_keys" USING (("auth"."uid"() = "user_id"));


CREATE POLICY "User can manage only their own API keys" ON "public"."users_provider_rent_api_keys" USING (("auth"."uid"() = "user_id")) WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "User can manage own settings" ON "public"."user_playground_settings" USING (("user_id" = "auth"."uid"())) WITH CHECK (("user_id" = "auth"."uid"()));


CREATE POLICY "User can read only their rented API keys" ON "public"."rent_api_keys" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM "public"."users_provider_rent_api_keys" "uprak"
  WHERE (("uprak"."rent_key_id" = "rent_api_keys"."id") AND ("uprak"."user_id" = "auth"."uid"())))));


CREATE POLICY "Users can create their own feedback" ON "public"."users_feedback" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can delete only their own tokens" ON "public"."users_oauth_tokens" FOR DELETE USING (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can delete their own custom auth data" ON "public"."user_provider_custom_auth" FOR DELETE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can delete their own data" ON "public"."users_provider_indexes" FOR DELETE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can delete their own feedback" ON "public"."users_feedback" FOR DELETE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can delete their own memory" ON "public"."users_memory" FOR DELETE USING (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can delete their own providers" ON "public"."users_providers" FOR DELETE TO "authenticated" USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can delete their own records" ON "public"."users_db_access" FOR DELETE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can delete their own requests" ON "public"."integration_requests" FOR DELETE USING (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can delete their own stripe records" ON "public"."users_stripe" FOR DELETE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can do anything with their own users_mcp rows" ON "public"."users_mcp" USING (("user_id" = "auth"."uid"())) WITH CHECK (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can insert their own custom auth data" ON "public"."user_provider_custom_auth" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can insert their own data" ON "public"."users_provider_indexes" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can insert their own memory" ON "public"."users_memory" FOR INSERT WITH CHECK (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can insert their own providers" ON "public"."users_providers" FOR INSERT TO "authenticated" WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can insert their own records" ON "public"."users_db_access" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can insert their own requests" ON "public"."integration_requests" FOR INSERT WITH CHECK (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can insert their own stripe records" ON "public"."users_stripe" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can insert their own tokens" ON "public"."users_oauth_tokens" FOR INSERT WITH CHECK (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can read their own custom auth data" ON "public"."user_provider_custom_auth" FOR SELECT USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can read their own data" ON "public"."users_provider_indexes" FOR SELECT USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can read their own feedback" ON "public"."users_feedback" FOR SELECT USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can read their own records" ON "public"."users_db_access" FOR SELECT USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can update only their own tokens" ON "public"."users_oauth_tokens" FOR UPDATE USING (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can update their own custom auth data" ON "public"."user_provider_custom_auth" FOR UPDATE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can update their own feedback" ON "public"."users_feedback" FOR UPDATE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can update their own memory" ON "public"."users_memory" FOR UPDATE USING (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can update their own providers" ON "public"."users_providers" FOR UPDATE TO "authenticated" USING (("auth"."uid"() = "user_id")) WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can update their own records" ON "public"."users_db_access" FOR UPDATE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can update their own requests" ON "public"."integration_requests" FOR UPDATE USING (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can update their own stripe records" ON "public"."users_stripe" FOR UPDATE USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can view their own API calls" ON "public"."api_calls" FOR SELECT USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can view their own memory" ON "public"."users_memory" FOR SELECT USING (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can view their own providers" ON "public"."users_providers" FOR SELECT TO "authenticated" USING (("auth"."uid"() = "user_id"));


CREATE POLICY "Users can view their own requests" ON "public"."integration_requests" FOR SELECT USING (("user_id" = "auth"."uid"()));


CREATE POLICY "Users can view their own stripe records" ON "public"."users_stripe" FOR SELECT USING (("auth"."uid"() = "user_id"));


CREATE POLICY "access_flow_actions_if_owner_or_shared" ON "public"."flow_actions" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM "public"."user_flows" "uf"
  WHERE (("uf"."id" = "flow_actions"."flow_id") AND (("uf"."user_id" = "auth"."uid"()) OR ("uf"."is_shared" = true))))));


CREATE POLICY "access_own_user_actions" ON "public"."users_provider_actions" USING (("user_id" = "auth"."uid"())) WITH CHECK (("user_id" = "auth"."uid"()));


CREATE POLICY "access_own_user_flows" ON "public"."user_flows" USING (("user_id" = "auth"."uid"())) WITH CHECK (("user_id" = "auth"."uid"()));


CREATE POLICY "access_user_related_action_scopes" ON "public"."provider_action_scopes" USING ((EXISTS ( SELECT 1
   FROM "public"."users_provider_actions" "upa"
  WHERE (("upa"."action_id" = "provider_action_scopes"."action_id") AND ("upa"."user_id" = "auth"."uid"()))))) WITH CHECK ((EXISTS ( SELECT 1
   FROM "public"."users_provider_actions" "upa"
  WHERE (("upa"."action_id" = "provider_action_scopes"."action_id") AND ("upa"."user_id" = "auth"."uid"())))));


CREATE POLICY "access_user_related_actions" ON "public"."provider_actions" USING ((EXISTS ( SELECT 1
   FROM "public"."users_provider_actions" "upa"
  WHERE (("upa"."action_id" = "provider_actions"."id") AND ("upa"."user_id" = "auth"."uid"()))))) WITH CHECK ((EXISTS ( SELECT 1
   FROM "public"."users_provider_actions" "upa"
  WHERE (("upa"."action_id" = "provider_actions"."id") AND ("upa"."user_id" = "auth"."uid"())))));


CREATE POLICY "access_user_related_flow_actions" ON "public"."flow_actions" USING ((EXISTS ( SELECT 1
   FROM "public"."user_flows" "uf"
  WHERE (("uf"."id" = "flow_actions"."flow_id") AND ("uf"."user_id" = "auth"."uid"()))))) WITH CHECK ((EXISTS ( SELECT 1
   FROM "public"."user_flows" "uf"
  WHERE (("uf"."id" = "flow_actions"."flow_id") AND ("uf"."user_id" = "auth"."uid"())))));


CREATE POLICY "access_user_related_scopes" ON "public"."provider_scopes" USING ((EXISTS ( SELECT 1
   FROM ("public"."provider_action_scopes" "pas"
     JOIN "public"."users_provider_actions" "upa" ON (("upa"."action_id" = "pas"."action_id")))
  WHERE (("pas"."scope_id" = "provider_scopes"."id") AND ("upa"."user_id" = "auth"."uid"()))))) WITH CHECK ((EXISTS ( SELECT 1
   FROM ("public"."provider_action_scopes" "pas"
     JOIN "public"."users_provider_actions" "upa" ON (("upa"."action_id" = "pas"."action_id")))
  WHERE (("pas"."scope_id" = "provider_scopes"."id") AND ("upa"."user_id" = "auth"."uid"())))));


ALTER TABLE "public"."api_calls" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."chat_messsages_metadata" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."chats_chats" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."chats_messages" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."contact_us_requests" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "delete_chats" ON "public"."chats_chats" FOR DELETE USING (("user_id" = "auth"."uid"()));


CREATE POLICY "delete_own_messages" ON "public"."flows_messages" FOR DELETE USING (("auth"."uid"() = "user_id"));


ALTER TABLE "public"."deploy_waitlist" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."external_mcp_repositories" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."flow_actions" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."flows_messages" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "insert_chats" ON "public"."chats_chats" FOR INSERT WITH CHECK (("user_id" = "auth"."uid"()));


CREATE POLICY "insert_own_messages" ON "public"."flows_messages" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));


ALTER TABLE "public"."integration_requests" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."jobs_export_batches" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."mcp_repositories" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."mcp_repository_deployments" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."omi_users" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."products_info" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."provider_action_scopes" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."provider_actions" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."provider_scopes" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."provider_tools" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."providers" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "public_read_providers_actions" ON "public"."provider_actions" FOR SELECT USING (true);


ALTER TABLE "public"."rent_api_keys" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "select_chats" ON "public"."chats_chats" FOR SELECT USING ((("is_shared" = true) OR ("user_id" = "auth"."uid"())));


CREATE POLICY "select_messages" ON "public"."chats_messages" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM "public"."chats_chats" "c"
  WHERE (("c"."id" = "chats_messages"."chat_id") AND (("c"."is_shared" = true) OR ("c"."user_id" = "auth"."uid"()))))));


CREATE POLICY "select_own_messages" ON "public"."flows_messages" FOR SELECT USING (("auth"."uid"() = "user_id"));


CREATE POLICY "select_user_flows_if_owner_or_shared" ON "public"."user_flows" FOR SELECT USING ((("user_id" = "auth"."uid"()) OR ("is_shared" = true)));


CREATE POLICY "update_chats" ON "public"."chats_chats" FOR UPDATE USING (("user_id" = "auth"."uid"()));


CREATE POLICY "update_own_messages" ON "public"."flows_messages" FOR UPDATE USING (("auth"."uid"() = "user_id")) WITH CHECK (("auth"."uid"() = "user_id"));


ALTER TABLE "public"."user_auth_codes" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_flow_runs" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_flow_schedules" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_flows" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_playground_settings" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_provider_custom_auth" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_tools_experimental" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_api_keys" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_beta" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_data_export" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_db_access" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_export_jobs" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_feedback" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_mcp" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_memory" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_oauth_tokens" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "users_oauth_tokens_insert" ON "public"."users_oauth_tokens" FOR INSERT WITH CHECK (("auth"."uid"() = "user_id"));


CREATE POLICY "users_oauth_tokens_select" ON "public"."users_oauth_tokens" USING (("auth"."uid"() = "user_id"));


ALTER TABLE "public"."users_provider_actions" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_provider_api_keys" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_provider_indexes" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_provider_rent_api_keys" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_providers" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_stripe" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_team_requests" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."users_waitlist" ENABLE ROW LEVEL SECURITY;


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";


GRANT ALL ON TABLE "public"."users_view" TO "anon";
GRANT ALL ON TABLE "public"."users_view" TO "authenticated";
GRANT ALL ON TABLE "public"."users_view" TO "service_role";


GRANT ALL ON FUNCTION "public"."get_current_user_meta"() TO "anon";
GRANT ALL ON FUNCTION "public"."get_current_user_meta"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_current_user_meta"() TO "service_role";


GRANT ALL ON FUNCTION "public"."get_tables_with_user_id"() TO "anon";
GRANT ALL ON FUNCTION "public"."get_tables_with_user_id"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_tables_with_user_id"() TO "service_role";


GRANT ALL ON TABLE "public"."providers" TO "anon";
GRANT ALL ON TABLE "public"."providers" TO "authenticated";
GRANT ALL ON TABLE "public"."providers" TO "service_role";


GRANT ALL ON TABLE "public"."users_providers" TO "anon";
GRANT ALL ON TABLE "public"."users_providers" TO "authenticated";
GRANT ALL ON TABLE "public"."users_providers" TO "service_role";


GRANT ALL ON TABLE "public"."top_connected_providers" TO "anon";
GRANT ALL ON TABLE "public"."top_connected_providers" TO "authenticated";
GRANT ALL ON TABLE "public"."top_connected_providers" TO "service_role";


GRANT ALL ON FUNCTION "public"."get_top_connected_providers"() TO "anon";
GRANT ALL ON FUNCTION "public"."get_top_connected_providers"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_top_connected_providers"() TO "service_role";


GRANT ALL ON TABLE "public"."users_stripe" TO "anon";
GRANT ALL ON TABLE "public"."users_stripe" TO "authenticated";
GRANT ALL ON TABLE "public"."users_stripe" TO "service_role";


GRANT ALL ON TABLE "public"."users_subscription_status_view" TO "anon";
GRANT ALL ON TABLE "public"."users_subscription_status_view" TO "authenticated";
GRANT ALL ON TABLE "public"."users_subscription_status_view" TO "service_role";


GRANT ALL ON FUNCTION "public"."get_user_subscription"() TO "anon";
GRANT ALL ON FUNCTION "public"."get_user_subscription"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_user_subscription"() TO "service_role";


GRANT ALL ON FUNCTION "public"."get_user_subscription"("user_id" "uuid") TO "anon";
GRANT ALL ON FUNCTION "public"."get_user_subscription"("user_id" "uuid") TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_user_subscription"("user_id" "uuid") TO "service_role";


GRANT ALL ON FUNCTION "public"."get_user_tools_secure"("user_id_param" "uuid") TO "anon";
GRANT ALL ON FUNCTION "public"."get_user_tools_secure"("user_id_param" "uuid") TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_user_tools_secure"("user_id_param" "uuid") TO "service_role";


GRANT ALL ON FUNCTION "public"."insert_provider_actions_for_all_users"("provider" "uuid") TO "anon";
GRANT ALL ON FUNCTION "public"."insert_provider_actions_for_all_users"("provider" "uuid") TO "authenticated";
GRANT ALL ON FUNCTION "public"."insert_provider_actions_for_all_users"("provider" "uuid") TO "service_role";


GRANT ALL ON FUNCTION "public"."strip_html_tags"("text_with_tags" "text") TO "anon";
GRANT ALL ON FUNCTION "public"."strip_html_tags"("text_with_tags" "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."strip_html_tags"("text_with_tags" "text") TO "service_role";


GRANT ALL ON TABLE "public"."api_calls" TO "anon";
GRANT ALL ON TABLE "public"."api_calls" TO "authenticated";
GRANT ALL ON TABLE "public"."api_calls" TO "service_role";


GRANT ALL ON SEQUENCE "public"."api_calls_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."api_calls_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."api_calls_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."chat_messsages_metadata" TO "anon";
GRANT ALL ON TABLE "public"."chat_messsages_metadata" TO "authenticated";
GRANT ALL ON TABLE "public"."chat_messsages_metadata" TO "service_role";


GRANT ALL ON SEQUENCE "public"."chat_messsages_metadata_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."chat_messsages_metadata_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."chat_messsages_metadata_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."chats_chats" TO "anon";
GRANT ALL ON TABLE "public"."chats_chats" TO "authenticated";
GRANT ALL ON TABLE "public"."chats_chats" TO "service_role";


GRANT ALL ON TABLE "public"."chats_messages" TO "anon";
GRANT ALL ON TABLE "public"."chats_messages" TO "authenticated";
GRANT ALL ON TABLE "public"."chats_messages" TO "service_role";


GRANT ALL ON SEQUENCE "public"."chats_messages_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."chats_messages_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."chats_messages_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."contact_us_requests" TO "anon";
GRANT ALL ON TABLE "public"."contact_us_requests" TO "authenticated";
GRANT ALL ON TABLE "public"."contact_us_requests" TO "service_role";


GRANT ALL ON SEQUENCE "public"."contact_us_requests_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."contact_us_requests_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."contact_us_requests_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."deploy_waitlist" TO "anon";
GRANT ALL ON TABLE "public"."deploy_waitlist" TO "authenticated";
GRANT ALL ON TABLE "public"."deploy_waitlist" TO "service_role";


GRANT ALL ON SEQUENCE "public"."deploy_waitlist_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."deploy_waitlist_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."deploy_waitlist_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."external_mcp_repositories" TO "anon";
GRANT ALL ON TABLE "public"."external_mcp_repositories" TO "authenticated";
GRANT ALL ON TABLE "public"."external_mcp_repositories" TO "service_role";


GRANT ALL ON SEQUENCE "public"."external_mcp_repositories_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."external_mcp_repositories_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."external_mcp_repositories_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."flow_actions" TO "anon";
GRANT ALL ON TABLE "public"."flow_actions" TO "authenticated";
GRANT ALL ON TABLE "public"."flow_actions" TO "service_role";


GRANT ALL ON SEQUENCE "public"."flow_actions_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."flow_actions_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."flow_actions_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."user_flow_runs" TO "anon";
GRANT ALL ON TABLE "public"."user_flow_runs" TO "authenticated";
GRANT ALL ON TABLE "public"."user_flow_runs" TO "service_role";


GRANT ALL ON TABLE "public"."flow_runs_view" TO "anon";
GRANT ALL ON TABLE "public"."flow_runs_view" TO "authenticated";
GRANT ALL ON TABLE "public"."flow_runs_view" TO "service_role";


GRANT ALL ON TABLE "public"."flows_messages" TO "anon";
GRANT ALL ON TABLE "public"."flows_messages" TO "authenticated";
GRANT ALL ON TABLE "public"."flows_messages" TO "service_role";


GRANT ALL ON SEQUENCE "public"."flows_messages_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."flows_messages_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."flows_messages_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."integration_requests" TO "anon";
GRANT ALL ON TABLE "public"."integration_requests" TO "authenticated";
GRANT ALL ON TABLE "public"."integration_requests" TO "service_role";


GRANT ALL ON SEQUENCE "public"."integration_request_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."integration_request_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."integration_request_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."jobs_export_batches" TO "anon";
GRANT ALL ON TABLE "public"."jobs_export_batches" TO "authenticated";
GRANT ALL ON TABLE "public"."jobs_export_batches" TO "service_role";


GRANT ALL ON TABLE "public"."mcp_repositories" TO "anon";
GRANT ALL ON TABLE "public"."mcp_repositories" TO "authenticated";
GRANT ALL ON TABLE "public"."mcp_repositories" TO "service_role";


GRANT ALL ON TABLE "public"."mcp_repository_deployments" TO "anon";
GRANT ALL ON TABLE "public"."mcp_repository_deployments" TO "authenticated";
GRANT ALL ON TABLE "public"."mcp_repository_deployments" TO "service_role";


GRANT ALL ON SEQUENCE "public"."mcp_repository_deployments_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."mcp_repository_deployments_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."mcp_repository_deployments_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."omi_users" TO "anon";
GRANT ALL ON TABLE "public"."omi_users" TO "authenticated";
GRANT ALL ON TABLE "public"."omi_users" TO "service_role";


GRANT ALL ON SEQUENCE "public"."omi_users_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."omi_users_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."omi_users_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."popular_providers_view" TO "anon";
GRANT ALL ON TABLE "public"."popular_providers_view" TO "authenticated";
GRANT ALL ON TABLE "public"."popular_providers_view" TO "service_role";


GRANT ALL ON TABLE "public"."products_info" TO "anon";
GRANT ALL ON TABLE "public"."products_info" TO "authenticated";
GRANT ALL ON TABLE "public"."products_info" TO "service_role";


GRANT ALL ON SEQUENCE "public"."products_info_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."products_info_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."products_info_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."provider_action_scopes" TO "anon";
GRANT ALL ON TABLE "public"."provider_action_scopes" TO "authenticated";
GRANT ALL ON TABLE "public"."provider_action_scopes" TO "service_role";


GRANT ALL ON TABLE "public"."provider_scopes" TO "anon";
GRANT ALL ON TABLE "public"."provider_scopes" TO "authenticated";
GRANT ALL ON TABLE "public"."provider_scopes" TO "service_role";


GRANT ALL ON SEQUENCE "public"."provider_action_scopes_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."provider_action_scopes_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."provider_action_scopes_id_seq" TO "service_role";


GRANT ALL ON SEQUENCE "public"."provider_action_scopes_id_seq1" TO "anon";
GRANT ALL ON SEQUENCE "public"."provider_action_scopes_id_seq1" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."provider_action_scopes_id_seq1" TO "service_role";


GRANT ALL ON TABLE "public"."provider_actions" TO "anon";
GRANT ALL ON TABLE "public"."provider_actions" TO "authenticated";
GRANT ALL ON TABLE "public"."provider_actions" TO "service_role";


GRANT ALL ON TABLE "public"."provider_actions_with_scopes_view" TO "anon";
GRANT ALL ON TABLE "public"."provider_actions_with_scopes_view" TO "authenticated";
GRANT ALL ON TABLE "public"."provider_actions_with_scopes_view" TO "service_role";


GRANT ALL ON TABLE "public"."provider_tools" TO "anon";
GRANT ALL ON TABLE "public"."provider_tools" TO "authenticated";
GRANT ALL ON TABLE "public"."provider_tools" TO "service_role";


GRANT ALL ON SEQUENCE "public"."provider_tools_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."provider_tools_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."provider_tools_id_seq" TO "service_role";


GRANT ALL ON SEQUENCE "public"."providers_actions_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."providers_actions_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."providers_actions_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."rent_api_keys" TO "anon";
GRANT ALL ON TABLE "public"."rent_api_keys" TO "authenticated";
GRANT ALL ON TABLE "public"."rent_api_keys" TO "service_role";


GRANT ALL ON SEQUENCE "public"."rent_api_keys_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."rent_api_keys_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."rent_api_keys_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."user_flows" TO "anon";
GRANT ALL ON TABLE "public"."user_flows" TO "authenticated";
GRANT ALL ON TABLE "public"."user_flows" TO "service_role";


GRANT ALL ON TABLE "public"."user_actions_flows_view" TO "anon";
GRANT ALL ON TABLE "public"."user_actions_flows_view" TO "authenticated";
GRANT ALL ON TABLE "public"."user_actions_flows_view" TO "service_role";


GRANT ALL ON TABLE "public"."users_provider_actions" TO "anon";
GRANT ALL ON TABLE "public"."users_provider_actions" TO "authenticated";
GRANT ALL ON TABLE "public"."users_provider_actions" TO "service_role";


GRANT ALL ON TABLE "public"."user_actions_view" TO "anon";
GRANT ALL ON TABLE "public"."user_actions_view" TO "authenticated";
GRANT ALL ON TABLE "public"."user_actions_view" TO "service_role";


GRANT ALL ON TABLE "public"."user_auth_codes" TO "anon";
GRANT ALL ON TABLE "public"."user_auth_codes" TO "authenticated";
GRANT ALL ON TABLE "public"."user_auth_codes" TO "service_role";


GRANT ALL ON TABLE "public"."users_oauth_tokens" TO "anon";
GRANT ALL ON TABLE "public"."users_oauth_tokens" TO "authenticated";
GRANT ALL ON TABLE "public"."users_oauth_tokens" TO "service_role";


GRANT ALL ON TABLE "public"."users_provider_indexes" TO "anon";
GRANT ALL ON TABLE "public"."users_provider_indexes" TO "authenticated";
GRANT ALL ON TABLE "public"."users_provider_indexes" TO "service_role";


GRANT ALL ON TABLE "public"."user_available_tools" TO "anon";
GRANT ALL ON TABLE "public"."user_available_tools" TO "authenticated";
GRANT ALL ON TABLE "public"."user_available_tools" TO "service_role";


GRANT ALL ON SEQUENCE "public"."user_flow_runs_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."user_flow_runs_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."user_flow_runs_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."user_flow_schedules" TO "anon";
GRANT ALL ON TABLE "public"."user_flow_schedules" TO "authenticated";
GRANT ALL ON TABLE "public"."user_flow_schedules" TO "service_role";


GRANT ALL ON SEQUENCE "public"."user_flow_schedules_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."user_flow_schedules_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."user_flow_schedules_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."user_monthly_usage_view" TO "anon";
GRANT ALL ON TABLE "public"."user_monthly_usage_view" TO "authenticated";
GRANT ALL ON TABLE "public"."user_monthly_usage_view" TO "service_role";


GRANT ALL ON TABLE "public"."user_playground_settings" TO "anon";
GRANT ALL ON TABLE "public"."user_playground_settings" TO "authenticated";
GRANT ALL ON TABLE "public"."user_playground_settings" TO "service_role";


GRANT ALL ON TABLE "public"."user_provider_custom_auth" TO "anon";
GRANT ALL ON TABLE "public"."user_provider_custom_auth" TO "authenticated";
GRANT ALL ON TABLE "public"."user_provider_custom_auth" TO "service_role";


GRANT ALL ON SEQUENCE "public"."user_provider_custom_auth_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."user_provider_custom_auth_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."user_provider_custom_auth_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."user_provider_scopes_view" TO "anon";
GRANT ALL ON TABLE "public"."user_provider_scopes_view" TO "authenticated";
GRANT ALL ON TABLE "public"."user_provider_scopes_view" TO "service_role";


GRANT ALL ON TABLE "public"."user_tools_experimental" TO "anon";
GRANT ALL ON TABLE "public"."user_tools_experimental" TO "authenticated";
GRANT ALL ON TABLE "public"."user_tools_experimental" TO "service_role";


GRANT ALL ON SEQUENCE "public"."user_tools_experimental_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."user_tools_experimental_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."user_tools_experimental_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_api_keys" TO "anon";
GRANT ALL ON TABLE "public"."users_api_keys" TO "authenticated";
GRANT ALL ON TABLE "public"."users_api_keys" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_api_keys_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_api_keys_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_api_keys_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_beta" TO "anon";
GRANT ALL ON TABLE "public"."users_beta" TO "authenticated";
GRANT ALL ON TABLE "public"."users_beta" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_beta_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_beta_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_beta_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_data_export" TO "anon";
GRANT ALL ON TABLE "public"."users_data_export" TO "authenticated";
GRANT ALL ON TABLE "public"."users_data_export" TO "service_role";


GRANT ALL ON TABLE "public"."users_db_access" TO "anon";
GRANT ALL ON TABLE "public"."users_db_access" TO "authenticated";
GRANT ALL ON TABLE "public"."users_db_access" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_db_acess_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_db_acess_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_db_acess_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_export_jobs" TO "anon";
GRANT ALL ON TABLE "public"."users_export_jobs" TO "authenticated";
GRANT ALL ON TABLE "public"."users_export_jobs" TO "service_role";


GRANT ALL ON TABLE "public"."users_feedback" TO "anon";
GRANT ALL ON TABLE "public"."users_feedback" TO "authenticated";
GRANT ALL ON TABLE "public"."users_feedback" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_feedback_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_feedback_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_feedback_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_mcp" TO "anon";
GRANT ALL ON TABLE "public"."users_mcp" TO "authenticated";
GRANT ALL ON TABLE "public"."users_mcp" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_mcp_repository_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_mcp_repository_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_mcp_repository_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_memory" TO "anon";
GRANT ALL ON TABLE "public"."users_memory" TO "authenticated";
GRANT ALL ON TABLE "public"."users_memory" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_memory_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_memory_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_memory_id_seq" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_provider_actions_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_provider_actions_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_provider_actions_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_provider_api_keys" TO "anon";
GRANT ALL ON TABLE "public"."users_provider_api_keys" TO "authenticated";
GRANT ALL ON TABLE "public"."users_provider_api_keys" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_provider_api_keys_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_provider_api_keys_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_provider_api_keys_id_seq" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_provider_indexes_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_provider_indexes_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_provider_indexes_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_provider_rent_api_keys" TO "anon";
GRANT ALL ON TABLE "public"."users_provider_rent_api_keys" TO "authenticated";
GRANT ALL ON TABLE "public"."users_provider_rent_api_keys" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_provider_rent_api_keys_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_provider_rent_api_keys_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_provider_rent_api_keys_id_seq" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_providers_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_providers_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_providers_id_seq" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_stripe_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_stripe_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_stripe_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_team_requests" TO "anon";
GRANT ALL ON TABLE "public"."users_team_requests" TO "authenticated";
GRANT ALL ON TABLE "public"."users_team_requests" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_team_requests_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_team_requests_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_team_requests_id_seq" TO "service_role";


GRANT ALL ON TABLE "public"."users_waitlist" TO "anon";
GRANT ALL ON TABLE "public"."users_waitlist" TO "authenticated";
GRANT ALL ON TABLE "public"."users_waitlist" TO "service_role";


GRANT ALL ON SEQUENCE "public"."users_waitlist_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_waitlist_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_waitlist_id_seq" TO "service_role";


ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";


ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";


ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";
