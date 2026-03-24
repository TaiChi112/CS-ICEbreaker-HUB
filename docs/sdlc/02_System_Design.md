# 02 System Design

## 1. Document Purpose

This document defines the system design baseline for CS-Icebreaker Hub, including runtime architecture, persistence model, and critical real-time interaction sequencing.

## 2. Architectural Overview

The platform is a web-based real-time game system with four primary technical subsystems:

- Next.js frontend for host/player interfaces and WebSocket client behavior.
- FastAPI backend for REST APIs, WebSocket channels, orchestration, and domain use cases.
- PostgreSQL for authoritative game state and transactional invariants.
- LLM provider integration via factory-backed adapter abstraction.

### 2.1 System Architecture Diagram

```mermaid
flowchart LR
    subgraph Client[Client Tier]
        UI[Next.js Frontend\nHost/Player UI]
    end

    subgraph Service[Application Tier]
        API[FastAPI REST Router\n/api/*]
        WS["FastAPI WS Router\n/ws/rooms/{room_code}"]
        UC[Application Use Cases\nCreate/Join/Generate/Claim/Score]
        HUB[Room Hub\nConnection Registry + Broadcast]
        LLMF[LLM Factory]
    end

    subgraph Data[Data Tier]
        DB[(PostgreSQL)]
    end

    subgraph External[External AI Tier]
        LLM[LLM Provider\nOpenAI or Mock Fallback]
    end

    UI -->|HTTPS JSON| API
    UI -->|WebSocket Events| WS
    API --> UC
    WS --> UC
    WS --> HUB
    UC --> DB
    API --> LLMF
    LLMF --> LLM
```

## 3. Clean Architecture Layering

### 3.1 Presentation Layer

- REST endpoints for room, question, and health workflows.
- WebSocket endpoint for room-scoped, low-latency signaling.

### 3.2 Application Layer

- Use cases coordinate room lifecycle, question generation/listing, claim operations, and scoring behavior.

### 3.3 Domain Layer

- Core entities and repository contracts define invariant boundaries and business-level interaction rules.

### 3.4 Infrastructure Layer

- SQLAlchemy repositories provide persistence behavior.
- Alembic migrations provide schema evolution.
- LLM providers are selected through a factory to isolate external dependency behavior.

## 4. Persistence Model

The implementation uses SQLAlchemy models that map directly to PostgreSQL relations.
The schema emphasizes room-centric state, event chronology, and claim arbitration.

### 4.1 Database ERD

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
        uuid question_id FK "UK to enforce single claim per question"
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

    USERS ||--o{ ROOMS : hosts
    USERS ||--o{ ROOM_PLAYERS : participates_as
    ROOMS ||--o{ ROOM_PLAYERS : contains
    ROOMS ||--o{ GAME_ROUNDS : has
    GAME_ROUNDS ||--o{ QUESTIONS : contains
    QUESTIONS ||--|| QUESTION_CLAIMS : claimed_once
    ROOM_PLAYERS ||--o{ QUESTION_CLAIMS : claims
    ROOMS ||--o{ SCORE_EVENTS : aggregates
    ROOM_PLAYERS ||--o{ SCORE_EVENTS : scorer
    ROOM_PLAYERS ||--o{ SCORE_EVENTS : target
```

## 5. Critical Runtime Sequence

The most critical race-sensitive path is concurrent question claim handling over WebSocket.
The design delegates arbitration to a unique database constraint on `question_claims.question_id`.

### 5.1 Sequence Diagram: WS Connection + First-Come Claim

```mermaid
sequenceDiagram
    autonumber
    participant P1 as Player A (Next.js)
    participant P2 as Player B (Next.js)
    participant WSR as FastAPI WS Router
    participant HUB as Room Hub
    participant UCC as ClaimQuestionUseCase
    participant REPO as Gameplay Repository
    participant DB as PostgreSQL

    P1->>WSR: Connect /ws/rooms/{room_code}?player_id=...&display_name=...
    WSR->>DB: Verify player membership in room
    DB-->>WSR: Membership valid
    WSR->>HUB: connect(room_code, player_id, websocket)
    HUB-->>P1: player.joined broadcast

    P2->>WSR: Connect /ws/rooms/{room_code}?player_id=...&display_name=...
    WSR->>DB: Verify player membership in room
    DB-->>WSR: Membership valid
    WSR->>HUB: connect(room_code, player_id, websocket)
    HUB-->>P1: player.joined broadcast
    HUB-->>P2: player.joined broadcast

    par Concurrent claim attempts
        P1->>WSR: {type: question.claim, payload: {questionId: Q1}}
        WSR->>UCC: execute(question_id=Q1, selector_player_id=P1)
        UCC->>REPO: claim_question_atomically(Q1, P1)
        REPO->>DB: INSERT question_claims(question_id=Q1, selector_player_id=P1)
        DB-->>REPO: Success (first writer)
        REPO-->>UCC: QuestionClaim
        UCC-->>WSR: Success
        WSR->>HUB: broadcast question.claimed
        HUB-->>P1: question.claimed
        HUB-->>P2: question.claimed
    and
        P2->>WSR: {type: question.claim, payload: {questionId: Q1}}
        WSR->>UCC: execute(question_id=Q1, selector_player_id=P2)
        UCC->>REPO: claim_question_atomically(Q1, P2)
        REPO->>DB: INSERT question_claims(question_id=Q1, selector_player_id=P2)
        DB-->>REPO: Unique constraint violation
        REPO-->>UCC: None
        UCC-->>WSR: AlreadyClaimedError
        WSR-->>P2: question.claim_rejected
    end
```

## 6. Concurrency and Consistency Strategy

- Race handling is resolved by a write-time unique constraint at persistence layer.
- Claim outcome is deterministic per question under concurrent pressure.
- Broadcast updates produce eventual room-wide visibility of accepted claims.

## 7. Design Risks and Forward Improvements

- WebSocket identity trust and room-bound claim validation require additional hardening.
- Event schema strictness should be tightened to prevent frontend/backend drift.
- Reconnection strategy and ordered refresh behavior should be formalized for resilient UX under network churn.

These items align with existing QA debt tracking and should be treated as high-priority reliability workstreams.
