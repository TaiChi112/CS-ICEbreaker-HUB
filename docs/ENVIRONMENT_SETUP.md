# Environment Variable Setup Guide

This document explains how to configure runtime environment variables for local development and testing.

## 1) Create Your Local Environment File

From the repository root, create a local `.env` file if it does not already exist:

```bash
cp .env.example .env
```

If `.env` already exists, update values in place.

## 2) Configure Application Basics

Set the following application settings:

- `APP_NAME`: Display name for the service.
- `APP_ENV`: Environment profile, usually `development` for local work.
- `APP_HOST`: Bind address for backend server (local default: `0.0.0.0`).
- `APP_PORT`: Backend port (default: `8000`).
- `FRONTEND_URL`: Frontend origin (default: `http://localhost:3000`).

## 3) Configure Database Connection

### DATABASE_URL format

`DATABASE_URL` uses this format for async PostgreSQL:

```text
postgresql+asyncpg://<username>:<password>@<host>:<port>/<database_name>
```

Example:

```text
postgresql+asyncpg://postgres:postgres@localhost:5432/cs_icebreaker_hub
```

### Field breakdown

- `<username>`: PostgreSQL user account.
- `<password>`: Password for that user.
- `<host>`: Database host (for local Docker typically `localhost`).
- `<port>`: PostgreSQL port (default `5432`).
- `<database_name>`: Database/schema name for this project.

## 4) Configure Security Secrets

The following secrets must be unique and high entropy:

- `SECRET_KEY`
- `JWT_SECRET`

### Generate secure secrets (recommended)

Option A: OpenSSL

```bash
openssl rand -hex 64
```

Option B: Python

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Generate two separate values and assign one to each variable.

### Security requirements

- Do not reuse secrets across projects.
- Do not share secrets in chat, commits, or screenshots.
- Rotate secrets if exposed.

## 5) Configure LLM Provider

Set `LLM_PROVIDER` to one of:

- `openai`
- `anthropic`

Then configure the matching provider key/model.

## 6) Obtain OPENAI_API_KEY

1. Go to https://platform.openai.com and create an account (or sign in).
2. Complete billing setup for API usage if your account requires it.
3. Open the API Keys page in your account dashboard.
4. Create a new secret key.
5. Copy the key once and store it securely.
6. Set it in `.env`:

```text
OPENAI_API_KEY=<your_openai_key>
OPENAI_MODEL=gpt-4o-mini
```

Notes:

- Keep keys server-side only.
- If compromised, revoke and regenerate immediately.

## 7) Obtain ANTHROPIC_API_KEY

1. Go to https://console.anthropic.com and create an account (or sign in).
2. Complete organization and billing setup as required.
3. Navigate to API Keys in the Anthropic console.
4. Create a new API key.
5. Copy and store the key securely.
6. Set it in `.env`:

```text
ANTHROPIC_API_KEY=<your_anthropic_key>
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

Notes:

- Keep provider keys out of frontend code and browser bundles.
- Revoke and replace keys on suspected leakage.

## 8) Configure Runtime and Room Behavior

Recommended defaults from current project configuration:

- `WS_PING_INTERVAL_SECONDS=20`
- `WS_PING_TIMEOUT_SECONDS=60`
- `MAX_ROOM_PLAYERS=200`
- `LLM_FALLBACK_ENABLED=true`
- `LOG_LEVEL=INFO`
- `ENABLE_STRUCTURED_LOGS=true`

Adjust only when testing specific reliability/performance scenarios.

## 9) Minimum Required Keys Checklist

Before running backend/frontend locally, confirm:

- `DATABASE_URL` is valid and reachable.
- `SECRET_KEY` is replaced with a secure random value.
- `JWT_SECRET` is replaced with a different secure random value.
- `LLM_PROVIDER` matches your selected API vendor.
- `OPENAI_API_KEY` is set when `LLM_PROVIDER=openai`.
- `ANTHROPIC_API_KEY` is set when `LLM_PROVIDER=anthropic`.

## 10) Verification Workflow

1. Start PostgreSQL.
2. Run backend migrations.
3. Start backend server and check health endpoint.
4. Start frontend and validate host/player flows.

If authentication, model generation, or DB access fails, re-check `.env` values first.

## 11) Secret Management Best Practices

- Keep `.env` local and untracked.
- Use environment-specific values (dev/staging/prod).
- Prefer secret managers for non-local environments.
- Never hardcode API keys in source files.
