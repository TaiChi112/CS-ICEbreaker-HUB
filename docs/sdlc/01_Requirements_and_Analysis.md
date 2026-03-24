# 01 Requirements and Analysis

## 1. Document Purpose

This document formalizes the software requirements and engineering analysis for CS-Icebreaker Hub.
It is intended for implementation, review, and traceability activities across backend, frontend, and platform operations.

## 2. Product Objectives

### 2.1 Vision

Deliver a real-time, low-latency multiplayer trivia experience that supports Computer Science networking and knowledge assessment.

### 2.2 Core Objective

Enable hosts and players to run topic-driven game rounds where:

- Hosts create and manage rooms.
- Players join via room code and compete to claim questions.
- Question generation is powered by an LLM abstraction layer.
- Score updates are propagated in real time.

### 2.3 Primary Operating Contexts

- MVP context: in-person classroom/workshop gameplay.
- Post-MVP context: remote and livestream-compatible gameplay.

## 3. Functional Requirements

### 3.1 Room Lifecycle

- FR-01: The system shall allow a host to create a room and receive room and host player identifiers.
- FR-02: The system shall allow players to join a room using a short room code.
- FR-03: The system shall expose room state, participant list, and leaderboard to authorized participants.

### 3.2 Question Lifecycle

- FR-04: The system shall allow host-triggered question batch generation by topic.
- FR-05: The system shall expose a list of currently claimable question prompts.
- FR-06: The system shall process question claim attempts over WebSocket messages.

### 3.3 Claim Arbitration

- FR-07: The system shall enforce first-come, first-served claim behavior at the database boundary.
- FR-08: The system shall reject duplicate claims for already claimed questions.
- FR-09: The system shall broadcast successful claim events to all room participants.

### 3.4 Scoring

- FR-10: The system shall support score events with scorer, target, points, and reason.
- FR-11: The system shall include score aggregation in leaderboard views.

### 3.5 Real-Time Channel

- FR-12: The system shall maintain room-scoped WebSocket channels.
- FR-13: The system shall support keepalive ping/pong semantics.
- FR-14: The system shall publish join/leave and game events to connected participants.

### 3.6 LLM Provider Abstraction

- FR-15: The system shall select LLM provider behavior through configuration.
- FR-16: The system shall use a provider factory abstraction for runtime provider resolution.
- FR-17: The system shall support fallback behavior when configured provider credentials are unavailable and fallback is enabled.

## 4. Non-Functional Requirements

### 4.1 Reliability

- NFR-01: WebSocket sessions shall tolerate routine network jitter via heartbeat timeout control.
- NFR-02: Critical game invariants shall be enforced by transactional and relational constraints.
- NFR-03: The application shall fail predictably when required configuration is missing.

### 4.2 Performance

- NFR-04: Room event fan-out shall remain bounded to room-scoped audiences.
- NFR-05: Claim arbitration latency shall be minimized by single-write atomic operations.

### 4.3 Maintainability

- NFR-06: Business rules shall remain framework-agnostic via Clean Architecture boundaries.
- NFR-07: Infrastructure concerns shall be encapsulated behind repository and provider interfaces.

### 4.4 Security

- NFR-08: Secrets and API credentials shall be sourced from environment variables only.
- NFR-09: State-changing actions shall be validated on the server side.

### 4.5 Observability

- NFR-10: Runtime logging shall be configurable by level and structured output mode.
- NFR-11: Health endpoints shall expose service and database status for diagnostics.

## 5. Real-Time LLM Trivia Mechanics Analysis

### 5.1 End-to-End Gameplay Loop

1. Host creates room and shares code.
2. Players join and establish room-scoped WebSocket channels.
3. Host generates question batch by topic through LLM-backed use case.
4. Players receive claimable prompts and issue `question.claim` messages.
5. Backend arbitrates race conditions and broadcasts accepted claims.
6. Score events update leaderboard state.

### 5.2 First-Come, First-Served Invariant

The claim model enforces uniqueness with a single-claim-per-question database constraint.
Current implementation path inserts into `question_claims` and relies on unique constraint conflict handling to resolve races.

Engineering implication:

- Correctness is preserved under concurrent claim attempts because duplicate inserts fail atomically.
- Throughput remains acceptable because arbitration occurs at the storage layer with minimal coordination overhead.

### 5.3 LLM Integration Analysis

The provider factory enables controlled operational behavior:

- `openai` path uses OpenAI key/model when configured.
- `anthropic` is configuration-recognized but currently not implemented for live inference.
- `mock` or fallback mode supports deterministic local development and test continuity.

Engineering implication:

- The system can progress independently of external provider availability in development.
- Provider parity work is required for full multi-provider production readiness.

### 5.4 Architectural Fit Assessment

The current design aligns with Clean Architecture expectations:

- Presentation layer remains transport-oriented (REST + WS).
- Application layer orchestrates use cases and validation semantics.
- Domain layer owns invariants and contracts.
- Infrastructure layer handles persistence and external providers.

This decomposition reduces coupling and supports incremental hardening without rewriting feature-level workflows.

## 6. Assumptions and Constraints

- PostgreSQL is the authoritative source of game state.
- WebSocket connectivity is available for real-time interactions.
- LLM-generated content quality is provider-dependent and non-deterministic.
- MVP favors delivery speed with transparent hardening backlog tracked separately.

## 7. Traceability Notes

This document synthesizes implemented behavior and requirement intent from:

- `docs/REQUIREMENTS.md`
- Backend API and WS routing flow
- SQLAlchemy model schema and repository claim arbitration logic
