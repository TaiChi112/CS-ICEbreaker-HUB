# 03 Implementation

## 1. Document Purpose

This document describes implementation structure and execution boundaries for the CS-Icebreaker Hub codebase.
It is intended to align contributors on current architectural decomposition and runtime entry points.

## 2. Backend Implementation (FastAPI + Clean Architecture)

The backend is implemented using a layered Clean Architecture model to keep business logic independent of transport and persistence concerns.

### 2.1 Layer Boundaries

- Presentation Layer (`app/presentation/*`)
  - REST endpoints under `/api/*`
  - WebSocket endpoints under `/ws/*`
  - Request/response schema shaping and protocol mapping
- Application Layer (`app/application/use_cases/*`)
  - Feature orchestration for room management, question generation, claiming, and scoring
  - Coordinates repositories and providers while preserving use-case-specific validation
- Domain Layer (`app/domain/*`)
  - Entities, errors, repository interfaces, and value-level rules
  - No dependency on FastAPI, SQLAlchemy, or external APIs
- Infrastructure Layer (`app/infrastructure/*`)
  - SQLAlchemy repositories and session management
  - Alembic integration and DB health checks
  - LLM provider implementations and provider factory

### 2.2 Runtime Composition

- Application bootstrap occurs in `app/main.py`.
- API router is mounted with `/api` prefix.
- WebSocket router is mounted with `/ws` prefix.
- Persistence and external integrations are resolved per use case via repository/provider construction.

### 2.3 API Discoverability

Dynamic API documentation is available through FastAPI Swagger UI:

- `/api/docs`

This endpoint should be treated as the canonical interactive reference for REST contract exploration during development and QA.

## 3. Frontend Implementation (Next.js App Router)

The frontend is implemented with Next.js App Router and TypeScript, with route-oriented composition for host and player workflows.

### 3.1 App Router Structure

- `app/layout.tsx`: global shell and metadata composition
- `app/page.tsx`: landing entry
- `app/host/page.tsx`: host session workflow
- `app/player/page.tsx`: player session workflow

### 3.2 Frontend Runtime Modules

- `lib/api.ts`: REST request wrapper and API access surface
- `lib/contracts.ts`: typed event and payload contracts
- `hooks/useRoomSocket.ts`: room-scoped WebSocket lifecycle and event processing
- `components/*`: reusable UI composition for gameplay interactions

### 3.3 Integration Model

- REST is used for room lifecycle, state retrieval, and question generation/listing.
- WebSocket is used for low-latency room presence and claim event propagation.
- Frontend routing and state transitions mirror backend room-code-centric workflows.

## 4. Implementation Notes for Contributors

- Keep protocol handlers thin and push orchestration into use cases.
- Preserve domain isolation from framework-specific imports.
- Treat schema and contract updates as cross-boundary changes requiring backend and frontend alignment.
- Include tests for behavior changes in claim arbitration, room membership, and websocket event handling.
