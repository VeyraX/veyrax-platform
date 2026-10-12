# Security Policy

VeyraX stores OAuth tokens and API keys on behalf of users, so we take security reports seriously.

## Reporting a vulnerability

**Please do not open a public GitHub issue for security problems.**

Report vulnerabilities privately via
[GitHub Security Advisories](https://github.com/VeyraX/veyrax-platform/security/advisories/new)
("Report a vulnerability" on the repository's *Security* tab).

Please include:

- a description of the issue and its impact;
- steps to reproduce or a proof of concept;
- affected files, endpoints or versions, if known.

We aim to acknowledge reports within 3 business days and will keep you updated on the fix.
Please give us reasonable time to release a fix before any public disclosure.

## Scope

In scope: the code in this repository — the `aci_server` backend, the `main` web app, integrations,
deployment configuration and the WhatsApp bridge.

Out of scope: vulnerabilities in third-party services that VeyraX integrates with (report those to the vendor),
and issues that require a compromised server or leaked `.env` file.

## Hardening tips for self-hosters

- Generate a unique `ENCRYPTION_KEY` (`openssl rand -hex 32`) — it encrypts all stored user credentials.
- Never expose `SUPABASE_SERVICE_KEY` to the browser; only `NEXT_PUBLIC_*` variables are public.
- Put Redis, Celery Flower and the WhatsApp bridge behind a firewall or authentication.
- Restrict `ALLOWED_ORIGINS` to your own domains.
