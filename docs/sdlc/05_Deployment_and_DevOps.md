# 05 Deployment and DevOps

## 1. Document Purpose

This document provides a deployment and DevOps baseline for CS-Icebreaker Hub.
It is intentionally environment-agnostic and defines recommended operational patterns for local, staging, and production workflows.

## 2. Deployment Strategy (Theoretical Baseline)

### 2.1 Target Topology

Recommended deployment units:

- Frontend service (Next.js)
- Backend service (FastAPI + Uvicorn/Gunicorn worker model)
- PostgreSQL database service
- Optional reverse proxy/ingress for TLS termination and routing

### 2.2 Environment Separation

Use independent environments with isolated secrets and databases:

- Development
- Staging
- Production

Configuration should be injected via environment variables and secret managers, not hardcoded in images.

## 3. Docker Compose Strategies

Docker Compose is recommended for local integration parity and simple environment bootstrapping.

### 3.1 Local Development Compose Pattern

- Run PostgreSQL as a dedicated service container.
- Run backend with source bind mount and reload support.
- Run frontend with source bind mount and development server.
- Use an internal Compose network for service-to-service communication.

### 3.2 Compose Operational Practices

- Use a dedicated `.env` per environment context.
- Define service health checks (DB readiness, API health).
- Use named volumes for persistent database state in local/dev.
- Keep resource limits explicit for reproducible team behavior.

### 3.3 Promotion Strategy

- Use Compose profiles or environment-specific override files for dev/staging/prod-like setups.
- Treat image tags as immutable release artifacts.
- Run migrations as explicit deployment steps before traffic cutover.

## 4. Continuous Integration (CI) Proposal

A baseline GitHub Actions workflow should validate backend and frontend on each pull request.

### 4.1 CI Objectives

- Prevent regressions by executing automated tests on every PR.
- Enforce consistent runtime/toolchain versions.
- Surface failures early before merge.

### 4.2 Proposed Workflow Structure

Trigger conditions:

- Pull requests to `main`
- Pushes to `main`

Jobs:

- Backend job
  - Setup Python
  - Install dependencies
  - Run lint/static checks (if configured)
  - Run backend tests
- Frontend job
  - Setup Bun (or Node + package manager strategy)
  - Install dependencies
  - Run frontend tests
  - Run frontend production build validation

### 4.3 Example GitHub Actions Workflow

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Run tests
        run: pytest

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2
        with:
          bun-version: "1.3.1"

      - name: Install dependencies
        run: bun install

      - name: Run tests
        run: bun test

      - name: Build
        run: bun run build
```

## 5. Release and Operational Controls (Recommended)

- Require passing CI checks before merge.
- Protect `main` branch with review and status checks.
- Version backend/frontend images with commit SHA tags.
- Maintain rollback procedure with previous image and migration policy.

## 6. Production Hardening Notes

- Add TLS, secure headers, and strict CORS policies at ingress.
- Add centralized logging and metrics (request latency, websocket concurrency, DB health).
- Add alerting for error-rate spikes and connectivity degradation.
- Run load testing for websocket fan-out and claim arbitration under expected concurrency.
