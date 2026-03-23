# CS-Icebreaker Hub

Real-time LLM trivia platform designed for Computer Science student networking and knowledge assessment.

## SDLC Overview

| Phase | Focus Area | Current Status |
| --- | --- | --- |
| 1 | Planning and Requirements | Completed |
| 2 | Architecture and Design | Completed |
| 3 | MVP Implementation | Completed |
| 4 | QA and Technical Audit | Completed (remediation pending) |
| 5 | Local Operations and Quick Start | Operational |
| 6 | Roadmap & Contributions | Open for contribution |

## Phase 1: Planning and Requirements

### Objective

Build a low-latency multiplayer platform where hosts generate topic-based trivia with LLM support and players compete in real time to claim and deliver questions.

### Source of Truth

- Product and engineering requirements are documented in [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).
- Delivery sequencing and milestones are documented in [docs/TASK_BREAKDOWN.md](docs/TASK_BREAKDOWN.md).

## Phase 2: System Architecture and Design

### Monorepo Structure

| Path | Responsibility |
| --- | --- |
| [backend](backend) | FastAPI service, domain logic, persistence, WebSocket orchestration |
| [frontend](frontend) | Next.js App Router UI, typed API/WS client integration |
| [shared/contracts](shared/contracts) | JSON schemas and shared contract definitions |
| [docs](docs) | Requirements, task plan, setup guidance |

### Backend Design (FastAPI + Clean Architecture)

Backend code is separated into explicit architectural layers:

- Domain layer: core entities, repository interfaces, invariants.
- Application layer: use cases and orchestration logic.
- Infrastructure layer: SQLAlchemy repositories, Alembic migrations, LLM adapters/factory.
- Presentation layer: HTTP routers and WebSocket handlers only.

This separation keeps transport concerns out of business logic and keeps business rules framework-agnostic.

### Frontend Design (Next.js)

- App Router-based UI with dedicated host and player flows.
- Type-safe API and WebSocket client modules.
- Tailwind CSS utility styling for responsive, mobile-first layouts.

### Contract-Driven Integration

- API and WS payload contracts are defined in [shared/contracts](shared/contracts).
- Frontend TypeScript interfaces are aligned to these schemas to minimize payload drift.
- Contract updates are treated as cross-boundary changes requiring backend and frontend review.

## Phase 3: Implementation Status

### MVP Foundation Status

The MVP foundation is implemented and wired end-to-end.

| Capability | Status | Notes |
| --- | --- | --- |
| Room create/join APIs | Implemented | Host and player onboarding flow is functional |
| Room state and leaderboard APIs | Implemented | Read model exposed for UI refresh and dashboarding |
| LLM question batch generation | Implemented | Factory Method provider selection with fallback support |
| Claimable question retrieval | Implemented | Unclaimed question prompts exposed for player selection |
| WebSocket room channel | Implemented | Join/leave events, ping/pong, and claim broadcasts |
| First-come question claim behavior | Implemented | DB uniqueness enforces single successful claimant |
| Frontend host/player dashboards | Implemented | Connected to API and WS endpoints |

### Technology Stack

| Layer | Technology |
| --- | --- |
| Backend API/WS | FastAPI, Uvicorn |
| Domain and persistence | SQLAlchemy, Alembic |
| Database | PostgreSQL |
| Frontend | Next.js 14, React 18, TypeScript |
| UI styling | Tailwind CSS |
| Testing | Pytest (backend), Bun/Vitest style frontend tests |

## Phase 4: Quality Assurance and Audit

### Audit Transparency

A dedicated QA and technical audit has already been performed across:

- Frontend WebSocket client behavior.
- Backend room hub and WebSocket routing.
- Use case boundaries and repository interactions.
- Shared contract consistency.

### Current QA Status

- Audit findings have been documented.
- Vulnerabilities and reliability gaps are known and pending remediation.
- Primary risk areas identified:
	- WebSocket stability and reconnection handling.
	- Claim path and room-boundary security validation.
	- UI loading/error state handling under adverse network conditions.
	- Contract strictness and event-schema consistency.

This repository intentionally preserves that transparency: MVP is operational, but hardening work remains before production-level confidence.

## Phase 5: Local Operations and Quick Start

### Prerequisites

- Python 3.12+
- Bun 1.3+ (or Node.js 20+ with npm)
- Docker Desktop
- PostgreSQL via Docker Compose

### 1) Environment Setup

From repository root:

```bash
cp .env.example .env
```

Set required values in `.env`:

- `DATABASE_URL`
- `LLM_PROVIDER`
- `OPENAI_API_KEY` (or provider-specific key)

### 2) Start PostgreSQL

```bash
docker compose up -d
```

### 3) Backend Operations

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements-dev.txt
.venv/Scripts/alembic.exe upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run backend tests:

```bash
cd backend
pytest
```

### 4) Frontend Operations

```bash
cd frontend
bun install
bun run dev
```

Run frontend tests:

```bash
cd frontend
bun test
```

### 5) Service Endpoints

| Service | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api |
| API Health | http://localhost:8000/api/health |
| DB Health | http://localhost:8000/api/health/db |

## Phase 6: Roadmap & Contributions

### Technical Debt (Help Wanted)

We welcome focused, production-hardening contributions. If you want to contribute, pick any open item below, include test coverage, and reference affected contract/schema changes in your PR description.

#### Backend

- [ ] [Critical] Enforce room-bound ownership checks for question claims before writing to `question_claims`.
- [ ] [High] Eliminate WebSocket identity spoofing by making server-side identity authoritative (ignore client-provided display names for trust decisions).
- [ ] [High] Standardize room code normalization for WebSocket routes and membership checks.
- [ ] [High] Harden WebSocket send/broadcast paths with broader transport exception handling and safe connection cleanup.
- [ ] [Medium] Emit explicit error responses for unsupported/unknown WebSocket message types.
- [ ] [Medium] Add structured disconnect reason payloads so clients can distinguish timeout, policy, and server-fault closures.
- [ ] [Medium] Add rate limiting and anti-spam controls for `question.claim` attempts.
- [ ] [Low] Use `last_seen` for stale connection pruning and room-presence observability metrics.

#### Frontend

- [ ] [High] Implement automatic WebSocket reconnection with bounded retry policy and exponential backoff.
- [ ] [High] Add cancellation/order guards for concurrent room refresh requests to prevent stale-state overwrites.
- [ ] [Medium] Add explicit loading states for initial room fetch and async actions (including question generation).
- [ ] [Medium] Preserve structured backend error details in UI feedback instead of generic fallback errors.
- [ ] [Medium] Add pending/disabled state for claim actions to prevent duplicate in-flight submissions.
- [ ] [Low] Replace placeholder reveal answers with authoritative backend-provided values.
- [ ] [Medium] Add guided recovery UX when room context parameters are missing or invalid.

#### Shared Contracts

- [ ] [High] Unify WebSocket event envelope naming across schemas and runtime payloads.
- [ ] [High] Tighten WebSocket payload schema constraints to detect field drift and enforce compatibility.
- [ ] [Medium] Standardize API/WS casing strategy and document mapping rules to reduce integration errors.

### Future Scaling (Post-MVP Features)

The roadmap below tracks post-MVP capabilities defined in the Future Scaling scope of [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).

- [ ] Remote Play: deliver selected questions directly to remote target players.
- [ ] Collision Prevention: enforce player availability states (Available/Answering) with accept/reject/queue behavior.
- [ ] Typed Answers: allow remote targets to submit answers through the UI.
- [ ] LLM Evaluator: evaluate user answers against expected answers and return correctness plus feedback.
- [ ] Remote/Livestream Session Mode: support distributed gameplay beyond in-person classroom constraints.

## Additional References

- [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)
- [docs/TASK_BREAKDOWN.md](docs/TASK_BREAKDOWN.md)
- [docs/SETUP_PHASE1.md](docs/SETUP_PHASE1.md)
