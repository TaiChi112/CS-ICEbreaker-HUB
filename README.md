# CS-Icebreaker Hub

> **Real-Time LLM Trivia Platform for Computer Science Teams**  
> Version `0.1.0` · MVP — Phase 1 Released

A full-stack, real-time multiplayer trivia system that enables a host to generate AI-driven question batches on any Computer Science topic and let players compete in a first-come, first-served race to claim and deliver questions — with live score propagation over WebSocket.

---

## Table of Contents

1. [Planning](#1-planning)
2. [Analysis](#2-analysis)
3. [Design](#3-design)
4. [Implementation](#4-implementation)
5. [Testing](#5-testing)
6. [Deployment](#6-deployment)
7. [Maintenance](#7-maintenance)

---

## 1. Planning

### 1.1 Problem Statement

Computer Science classrooms, workshops, and remote teams often lack an engaging, low-setup mechanism to break the ice and assess peer knowledge simultaneously. Existing quiz tools are generic, lack real-time interaction, and require manual question preparation.

**CS-Icebreaker Hub** solves this by providing a purpose-built, LLM-powered trivia platform where any host can spin up a room in seconds, generate a contextual question batch on demand, and let participants race to claim and answer questions — all with live feedback on a shared leaderboard.

### 1.2 Core Objectives

| Priority | Objective |
|---|---|
| P0 | Host-managed room lifecycle with a shareable short code |
| P0 | LLM-generated question batches from a configurable provider |
| P0 | First-come, first-served atomic question claiming over WebSocket |
| P0 | Real-time event propagation (join, leave, claim, score) |
| P1 | Leaderboard aggregation and live score updates |
| P2 | Remote / livestream gameplay mode (post-MVP) |

### 1.3 Technology Stack Rationale

| Layer | Technology | Rationale |
|---|---|---|
| **Backend API** | FastAPI 0.116 + Python 3.12 | Native async I/O, first-class WebSocket support, automatic OpenAPI docs |
| **Frontend** | Next.js 15 + React 18 + TypeScript | App Router, SSR/CSR flexibility, strong routing ergonomics |
| **Package Manager** | Bun 1.x | Fast install and test runner for the frontend monorepo |
| **Database** | PostgreSQL 16 | Transactional claim arbitration via unique constraints; ACID reliability |
| **ORM / Migrations** | SQLAlchemy 2.0 + Alembic | Async-native ORM; versioned, reversible schema evolution |
| **LLM Integration** | OpenAI API (gpt-4o-mini default) | Mature Chat Completions API; model is swappable via config |
| **Styling** | Tailwind CSS v4 | Utility-first, mobile-first responsive UI with zero runtime overhead |
| **Containerization** | Docker Compose | Reproducible local dev environment; promotes parity with production |

### 1.4 Operating Context

- **MVP**: In-person classroom or workshop icebreaker (physical Q&A delivery).
- **Post-MVP**: Remote and livestream-compatible gameplay with typed answers and LLM answer evaluation.

---

## 2. Analysis

### 2.1 Stakeholders and User Roles

| Role | Description |
|---|---|
| **Host** | Creates the room, generates question batches, monitors room state and leaderboard |
| **Player** | Joins via room code, claims questions first-come, delivers Q&A, receives scores |
| **System Admin** | Configures environment variables, LLM provider, and deployment topology |

### 2.2 Functional Requirements

#### Room Lifecycle
- **FR-01** — Host creates a room and receives `room_id`, `room_code`, and `player_id`.
- **FR-02** — Players join a room using the short room code and receive session identifiers.
- **FR-03** — Room state (status, participant list, leaderboard) is exposed to authorized participants.

#### Question Lifecycle
- **FR-04** — Host triggers LLM-backed question batch generation by topic (1–20 questions).
- **FR-05** — Claimable question prompts (without answers) are listed for players.
- **FR-06** — Players submit `question.claim` events over WebSocket.

#### Claim Arbitration
- **FR-07** — First-come, first-served semantics are enforced at the database boundary.
- **FR-08** — Duplicate claims for the same question are rejected with `question.claim_rejected`.
- **FR-09** — Successful claims are broadcast room-wide as `question.claimed`.

#### Scoring
- **FR-10** — Score events record scorer, target, points, and textual reason.
- **FR-11** — Leaderboard is computed from aggregated score events per room.

#### Real-Time Channel
- **FR-12** — Room-scoped WebSocket channels persist for connected participants.
- **FR-13** — Ping / pong keepalive semantics prevent stale connection accumulation.
- **FR-14** — `player.joined` and `player.left` events are broadcast on connect / disconnect.

#### LLM Provider
- **FR-15** — Provider is selected via `LLM_PROVIDER` environment variable.
- **FR-16** — A factory resolves the runtime provider implementation.
- **FR-17** — A mock fallback provider supports development without external credentials.

### 2.3 Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Reliability | WebSocket sessions tolerate jitter via configurable heartbeat timeout |
| NFR-02 | Reliability | Claim invariants are enforced by PostgreSQL unique constraints |
| NFR-03 | Performance | Room event fan-out is bounded to room-scoped audiences |
| NFR-04 | Performance | Claim arbitration latency minimized by single-write atomic DB operation |
| NFR-05 | Maintainability | Business rules are framework-agnostic (Clean Architecture) |
| NFR-06 | Security | All secrets sourced from environment variables only |
| NFR-07 | Security | State-changing actions validated server-side |
| NFR-08 | Observability | Health endpoints expose service and DB status |
| NFR-09 | Observability | Structured logging with configurable level |

---

## 3. Design

### 3.1 Architectural Style

The system follows **Clean Architecture** (Robert C. Martin) with a strict four-layer dependency rule: outer layers depend on inner layers; inner layers have no knowledge of outer layers.

```mermaid
flowchart TD
    subgraph Presentation["Presentation Layer"]
        REST["REST Router\n/api/*"]
        WS["WebSocket Router\n/ws/rooms/{room_code}"]
    end

    subgraph Application["Application Layer"]
        UC["Use Cases\nCreateRoom · JoinRoom · GenerateQuestionBatch\nClaimQuestion · RecordScore · GetRoomState"]
    end

    subgraph Domain["Domain Layer"]
        ENT["Entities\nRoom · RoomPlayer · GameRound\nQuestion · QuestionClaim · ScoreEvent"]
        REPO_I["Repository Interfaces\nGameplayRepository · QuestionRepository · RoomRepository"]
        LLM_I["LLM Interface\nLlmProvider"]
    end

    subgraph Infrastructure["Infrastructure Layer"]
        DB_REPO["SQLAlchemy Repositories"]
        LLM_PROV["LLM Providers\nOpenAiLlmProvider · MockLlmProvider"]
        DB[("PostgreSQL")]
        OPENAI["OpenAI API"]
    end

    Presentation --> Application
    Application --> Domain
    Infrastructure --> Domain
    DB_REPO --> DB
    LLM_PROV --> OPENAI
```

### 3.2 Full System Architecture

```mermaid
flowchart LR
    subgraph Client["Client Tier"]
        UI["Next.js Frontend\nHost Dashboard · Player View · Landing"]
    end

    subgraph Service["Application Tier · FastAPI"]
        API["REST Router\n/api/*"]
        WSR["WS Router\n/ws/rooms/{room_code}"]
        HUB["RoomHub\nConnection Registry + Broadcast"]
        UC["Use Cases"]
        LLMF["LLM Factory"]
    end

    subgraph Data["Data Tier"]
        PG[("PostgreSQL 16\ncs_icebreaker_hub")]
    end

    subgraph External["External AI Tier"]
        LLM["OpenAI\ngpt-4o-mini"]
    end

    UI -->|"HTTPS JSON"| API
    UI -->|"WebSocket Events"| WSR
    API --> UC
    WSR --> UC
    WSR --> HUB
    UC --> PG
    API --> LLMF
    LLMF --> LLM
```

### 3.3 Design Patterns

| Pattern | Location | Description |
|---|---|---|
| **Factory Method** (GoF) | `infrastructure/llm/factory.py` | `create_llm_provider()` resolves `OpenAiLlmProvider` or `MockLlmProvider` at runtime based on configuration |
| **Repository** (DDD) | `domain/repositories.py`, `domain/question_repositories.py` | `Protocol`-based interfaces decouple use cases from SQLAlchemy; swappable without domain changes |
| **Use Case / Command** (Clean Arch) | `application/use_cases/*` | Each use case is a single-responsibility dataclass with an `async execute()` method |
| **Hub (Mediator variant)** (GoF) | `presentation/ws/room_hub.py` | `RoomHub` manages all active WebSocket connections, keyed by `room_code → player_id`, and provides targeted and broadcast messaging |
| **Singleton** (GoF) | `room_hub.py`, `get_settings()` | `room_hub` is a module-level singleton; `get_settings()` is memoized via `@lru_cache` |
| **Strategy** (GoF) | `LlmProvider` Protocol | Interchangeable LLM implementations (`OpenAI`, `Mock`, future `Anthropic`) behind a common interface |
| **Custom Hook** (React) | `hooks/useRoomSocket.ts` | Encapsulates WebSocket lifecycle, heartbeat, and claim dispatch for frontend consumers |

### 3.4 Data Model (ERD)

```mermaid
erDiagram
    USERS {
        uuid id PK
        string display_name
        datetime created_at
    }

    ROOMS {
        uuid id PK
        string room_code UK
        uuid host_user_id FK
        string status
        datetime created_at
    }

    ROOM_PLAYERS {
        uuid id PK
        uuid room_id FK
        uuid user_id FK
        string role
        datetime joined_at
    }

    GAME_ROUNDS {
        uuid id PK
        uuid room_id FK
        string topic
        string status
        datetime created_at
    }

    QUESTIONS {
        uuid id PK
        uuid round_id FK
        text prompt
        text answer
        datetime created_at
    }

    QUESTION_CLAIMS {
        uuid id PK
        uuid question_id FK "UK — enforces single claim per question"
        uuid selector_player_id FK
        datetime claimed_at
    }

    SCORE_EVENTS {
        uuid id PK
        uuid room_id FK
        uuid scorer_player_id FK
        uuid target_player_id FK
        int points
        string reason
        datetime created_at
    }

    USERS ||--o{ ROOMS : "hosts"
    USERS ||--o{ ROOM_PLAYERS : "participates as"
    ROOMS ||--o{ ROOM_PLAYERS : "contains"
    ROOMS ||--o{ GAME_ROUNDS : "has"
    GAME_ROUNDS ||--o{ QUESTIONS : "contains"
    QUESTIONS ||--|| QUESTION_CLAIMS : "claimed once"
    ROOM_PLAYERS ||--o{ QUESTION_CLAIMS : "claims"
    ROOMS ||--o{ SCORE_EVENTS : "aggregates"
    ROOM_PLAYERS ||--o{ SCORE_EVENTS : "scorer"
    ROOM_PLAYERS ||--o{ SCORE_EVENTS : "target"
```

### 3.5 Critical Runtime Sequence — Concurrent Claim Arbitration

```mermaid
sequenceDiagram
    autonumber
    participant P1 as Player A (Next.js)
    participant P2 as Player B (Next.js)
    participant WSR as FastAPI WS Router
    participant HUB as RoomHub
    participant UCC as ClaimQuestionUseCase
    participant REPO as GameplayRepository
    participant DB as PostgreSQL

    P1->>WSR: Connect /ws/rooms/{room_code}?player_id=...
    WSR->>DB: Verify player membership
    DB-->>WSR: Valid
    WSR->>HUB: connect(room_code, player_id, websocket)
    HUB-->>P1: player.joined broadcast

    P2->>WSR: Connect /ws/rooms/{room_code}?player_id=...
    WSR->>DB: Verify player membership
    DB-->>WSR: Valid
    WSR->>HUB: connect(room_code, player_id, websocket)
    HUB-->>P1: player.joined broadcast
    HUB-->>P2: player.joined broadcast

    par Concurrent claim race
        P1->>WSR: question.claim {questionId: Q1}
        WSR->>UCC: execute(Q1, P1)
        UCC->>REPO: claim_question_atomically(Q1, P1)
        REPO->>DB: INSERT question_claims (Q1, P1)
        DB-->>REPO: OK — first writer wins
        REPO-->>UCC: QuestionClaim
        UCC-->>WSR: Success
        WSR->>HUB: broadcast question.claimed
        HUB-->>P1: question.claimed
        HUB-->>P2: question.claimed
    and
        P2->>WSR: question.claim {questionId: Q1}
        WSR->>UCC: execute(Q1, P2)
        UCC->>REPO: claim_question_atomically(Q1, P2)
        REPO->>DB: INSERT question_claims (Q1, P2)
        DB-->>REPO: Unique constraint violation
        REPO-->>UCC: None
        UCC-->>WSR: AlreadyClaimedError
        WSR-->>P2: question.claim_rejected
    end
```

### 3.6 WebSocket Event Envelope

All WebSocket messages conform to a typed envelope contract:

```
{ "type": "<event_type>", "payload": { ... }, "occurredAt": "<ISO-8601>" }
```

| Event Type | Direction | Description |
|---|---|---|
| `player.joined` | Server → All | A player successfully connected to the room |
| `player.left` | Server → All | A player disconnected from the room |
| `question.claim` | Client → Server | Player attempts to claim a question |
| `question.claimed` | Server → All | Claim accepted; broadcast to all participants |
| `question.claim_rejected` | Server → Sender | Claim denied (already taken or missing payload) |
| `ping` | Client → Server | Keepalive heartbeat (every 15 s) |
| `pong` | Server → Sender | Keepalive acknowledgement |

---

## 4. Implementation

### 4.1 Repository Structure

```
Game-Activity/
├── backend/                        # FastAPI Python service
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py           # Pydantic-Settings configuration (lru_cache)
│   │   ├── domain/                 # Framework-agnostic business layer
│   │   │   ├── entities.py         # Frozen dataclasses: Room, Player, Question, Claim, Score
│   │   │   ├── repositories.py     # GameplayRepository Protocol
│   │   │   ├── question_repositories.py
│   │   │   ├── room_repositories.py
│   │   │   └── llm.py              # LlmProvider Protocol + GeneratedQuestion
│   │   ├── application/
│   │   │   └── use_cases/          # One file per use case
│   │   │       ├── create_room.py
│   │   │       ├── join_room.py
│   │   │       ├── get_room_state.py
│   │   │       ├── generate_question_batch.py  ← AI-Native use case
│   │   │       ├── list_claimable_questions.py
│   │   │       ├── claim_question.py
│   │   │       └── record_score.py
│   │   ├── infrastructure/
│   │   │   ├── db/
│   │   │   │   ├── models.py       # SQLAlchemy ORM models
│   │   │   │   ├── session.py      # Async session factory
│   │   │   │   ├── mappers.py      # ORM → Domain entity mappers
│   │   │   │   └── repositories/   # Concrete repository implementations
│   │   │   └── llm/
│   │   │       ├── factory.py      # LLM Factory Method
│   │   │       ├── openai_provider.py
│   │   │       └── mock_provider.py
│   │   └── presentation/
│   │       ├── api/
│   │       │   ├── router.py       # REST endpoints
│   │       │   └── schemas.py      # Pydantic request/response schemas
│   │       └── ws/
│   │           ├── router.py       # WebSocket endpoint + event loop
│   │           └── room_hub.py     # RoomHub connection manager
│   ├── alembic/                    # Schema migration scripts
│   ├── tests/                      # pytest test suite (unit + integration)
│   └── requirements.txt
├── frontend/                       # Next.js 15 TypeScript application
│   ├── app/
│   │   ├── page.tsx                # Landing — create / join room
│   │   ├── host/page.tsx           # Host Dashboard — generate, monitor, leaderboard
│   │   └── player/page.tsx         # Player View — claim questions
│   ├── components/
│   │   └── QuestionRevealCard.tsx
│   ├── hooks/
│   │   └── useRoomSocket.ts        # WebSocket lifecycle custom hook
│   ├── lib/
│   │   ├── api.ts                  # REST + WS URL helpers
│   │   └── contracts.ts            # Shared TypeScript type contracts
│   └── tests/                      # Vitest unit tests
├── shared/
│   └── contracts/                  # Language-agnostic API/WS schema definitions
├── docs/
│   ├── REQUIREMENTS.md
│   ├── TASK_BREAKDOWN.md
│   └── sdlc/                       # Formal SDLC phase documents
│       ├── 01_Requirements_and_Analysis.md
│       ├── 02_System_Design.md
│       ├── 03_Implementation.md
│       ├── 04_Testing_and_QA.md
│       ├── 05_Deployment_and_DevOps.md
│       └── 06_Maintenance_and_Evolution.md
└── docker-compose.yml              # PostgreSQL service for local development
```

### 4.2 AI-Native Component — `GenerateQuestionBatchUseCase`

This is the system's core AI-native use case. It:

1. Validates the host's authorization within the target room.
2. Delegates to `LlmProvider.generate_question_batch(topic, batch_size)`.
3. Persists a new `GameRound` with the returned `Question` records atomically.

The `LlmProvider` interface is satisfied at runtime by `OpenAiLlmProvider`, which constructs a structured JSON prompt for `gpt-4o-mini` and parses the response into typed `GeneratedQuestion` objects. A `MockLlmProvider` is always available for development and CI environments without API keys.

### 4.3 REST API Surface

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Service liveness probe |
| `GET` | `/api/health/db` | Database connectivity probe |
| `POST` | `/api/rooms` | Create a new room (host) |
| `POST` | `/api/rooms/join` | Join an existing room by code |
| `GET` | `/api/rooms/{room_code}` | Get room state, players, and leaderboard |
| `POST` | `/api/rooms/{room_code}/questions/generate` | Generate LLM question batch (host only) |
| `GET` | `/api/rooms/{room_code}/questions` | List claimable question prompts |
| `WS` | `/ws/rooms/{room_code}` | Room-scoped real-time channel |

### 4.4 Key Configuration Variables

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cs_icebreaker_hub
LLM_PROVIDER=openai                  # openai | mock | anthropic (stub)
LLM_FALLBACK_ENABLED=true
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
WS_PING_TIMEOUT_SECONDS=60
MAX_ROOM_PLAYERS=200
LOG_LEVEL=INFO
ENABLE_STRUCTURED_LOGS=true
```

---

## 5. Testing

### 5.1 Backend — pytest

**Frameworks**: `pytest`, `pytest-asyncio`, `httpx` (ASGI test client)

| Test File | Scope | Type |
|---|---|---|
| `test_domain_entities.py` | Domain entity construction and invariants | Unit |
| `test_llm_factory.py` | LLM factory provider resolution | Unit |
| `test_generate_question_batch_use_case.py` | Question generation use case with mocked LLM | Unit |
| `test_use_cases.py` | Claim and score use cases with mocked repositories | Unit |
| `test_health.py` | `/api/health` endpoint response | Integration |
| `test_room_api_integration.py` | Room create / join / state REST flows | Integration |
| `test_question_generation_api_integration.py` | Question generation REST flow | Integration |
| `test_room_ws_integration.py` | WebSocket connect, claim, and disconnect flows | Integration |

**Run backend tests:**
```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

### 5.2 Frontend — Vitest

**Frameworks**: `vitest`, `@testing-library/react`, `@testing-library/user-event`, `jsdom`

| Test File | Scope | Type |
|---|---|---|
| `landing-contracts.test.ts` | TypeScript contract shape validation | Unit |
| `api-utils.test.ts` | API URL construction utilities | Unit |

**Run frontend tests:**
```bash
cd frontend
bun install
bun test
```

### 5.3 End-to-End Testing

> **Status**: [In Progress] — E2E tooling (e.g., Playwright) not yet configured.

**Intended scope:**
- Host creates room → Player joins → Host generates questions → Player claims → Score submitted → Leaderboard updated.
- Network interruption and WebSocket reconnection recovery UX.
- Concurrent claim race condition validation under load.

---

## 6. Deployment

### 6.1 Local Development (Docker Compose)

Start the PostgreSQL database:

```bash
docker compose up -d postgres
```

Start the backend:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Start the frontend:

```bash
cd frontend
bun install
bun run dev        # http://localhost:3000
```

### 6.2 Environment Topology

```mermaid
flowchart LR
    subgraph Local["Local / Development"]
        DC["Docker Compose\nPostgreSQL 16"]
        BE_DEV["uvicorn --reload\nbackend :8000"]
        FE_DEV["next dev\nfrontend :3000"]
    end

    subgraph Staging["Staging (Proposed)"]
        BE_STG["FastAPI Container\n+ Gunicorn Worker"]
        FE_STG["Next.js Container"]
        PG_STG[("PostgreSQL\nManaged")]
    end

    subgraph Production["Production (Proposed)"]
        PROXY["Reverse Proxy\n(TLS Termination)"]
        BE_PRD["FastAPI Service"]
        FE_PRD["Next.js Service"]
        PG_PRD[("PostgreSQL\nManaged HA")]
    end

    Local -->|promote image| Staging
    Staging -->|promote image| Production
```

### 6.3 CI Pipeline (Proposed — GitHub Actions)

```mermaid
flowchart LR
    PR["Pull Request\nto main"] --> CI

    subgraph CI["GitHub Actions"]
        B["Backend Job\nPython 3.12\npip install → pytest"]
        F["Frontend Job\nBun 1.x\nbun install → vitest → next build"]
    end

    CI -->|all checks pass| Merge["Merge to main"]
    Merge --> Tag["Tag image\ncommit SHA"]
    Tag --> Deploy["Deploy to Staging"]
```

**Trigger conditions**: Pull requests and pushes to `main`.

> **Status**: CI workflow YAML is defined in `docs/sdlc/05_Deployment_and_DevOps.md`. GitHub Actions workflow file is not yet committed to `.github/workflows/`.

### 6.4 Production Hardening Checklist

- [ ] TLS termination and strict CORS policy at ingress layer
- [ ] Centralized structured logging with room/player correlation fields
- [ ] Metrics: active rooms, WebSocket concurrency, DB query latency, claim throughput
- [ ] Alerting on error-rate spikes and DB connectivity degradation
- [ ] Load testing WebSocket fan-out under expected classroom concurrency

---

## 7. Maintenance

### 7.1 Known Technical Debt

#### Backend (Priority)
- `[Critical]` Enforce room-bound ownership checks for `question.claim` before writing to `question_claims`.
- `[High]` Eliminate WebSocket identity spoofing — make server-side identity authoritative.
- `[High]` Standardize `room_code` normalization across all WebSocket and membership paths.
- `[High]` Harden broadcast paths with broader transport exception handling.

#### Frontend (Priority)
- `[High]` Implement automatic WebSocket reconnection with bounded retry and exponential backoff.
- `[High]` Add cancellation guards for concurrent room-refresh requests.
- `[Medium]` Add explicit loading states for room fetch and question generation actions.

#### Shared Contracts
- `[High]` Unify WebSocket event envelope naming between backend schemas and frontend `contracts.ts`.
- `[High]` Tighten payload schema constraints to detect field drift at compile time.

### 7.2 Post-MVP Roadmap

```mermaid
flowchart LR
    MVP["Phase 1 — MVP\n✅ Room lifecycle\n✅ LLM question gen\n✅ Atomic claim\n✅ Real-time events\n✅ Leaderboard"] -->
    P2["Phase 2 — Remote Play\nDirect question delivery\nPlayer availability states\nTyped answer submission"] -->
    P3["Phase 3 — LLM Evaluator\nAI-graded typed answers\nCorrectness + feedback\nAuto scoring"] -->
    P4["Phase 4 — Scale & Ops\nCI quality gates\nObservability dashboards\nLoad-tested WebSocket fan-out"]
```

### 7.3 Observability Standards

- **Log levels**: configurable via `LOG_LEVEL` (`DEBUG` / `INFO` / `WARNING` / `ERROR`).
- **Structured output**: enabled via `ENABLE_STRUCTURED_LOGS=true`.
- **Recommended correlation fields**: `request_id`, `room_code`, `room_id`, `player_id`, `event_type`.
- **Operational metrics** (recommended): active rooms, active sockets per room, broadcast latency, claim accept/reject rates, DB health.

### 7.4 Change Management

- Use small, single-workstream pull requests.
- Include architecture-impact notes for contract, schema, and protocol changes.
- Synchronize SDLC documents (`docs/sdlc/`) with all implementation changes.
- Require regression tests for changes affecting WebSocket routing, claim arbitration, or scoring logic.

---

## Quick Start

```bash
# 1. Clone and configure
git clone <repository-url>
cd Game-Activity
cp .env.example .env
# Edit .env — set OPENAI_API_KEY (or leave LLM_FALLBACK_ENABLED=true)

# 2. Start database
docker compose up -d postgres

# 3. Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 4. Frontend (new terminal)
cd frontend
bun install
bun run dev
```

Open **http://localhost:3000** — create a room as host, join as a player, generate questions, and start playing.

---

*Documentation maintained in `docs/sdlc/`. API reference auto-generated at `http://localhost:8000/docs` (Swagger UI) when backend is running.*
