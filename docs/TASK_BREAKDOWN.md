# CS-Icebreaker Hub - Task Breakdown

## Development Plan (Pre-Code to Phase Delivery)

## Phase 0 - Foundation and Alignment
1. Confirm product scope and feature boundaries for MVP vs future scaling.
2. Confirm stack selection (FastAPI + Next.js + PostgreSQL) and runtime versions.
3. Finalize environment variable contract and secrets onboarding.
4. Establish repository standards (branching, PR checklist, commit style, issue templates).

Deliverables:
- Approved requirements and architecture docs.
- Agreed local development workflow.

## Phase 1 - Project Bootstrap and Core Skeleton
1. Initialize backend project structure with Clean Architecture folders.
2. Initialize frontend Next.js app with mobile-first baseline layout.
3. Add shared contracts folder for API/WebSocket event schemas.
4. Set up linting, formatting, and test frameworks for backend/frontend.
5. Configure local PostgreSQL and migration tooling.

Deliverables:
- Running backend and frontend skeletons.
- Database connectivity verified.
- Baseline quality tooling enforced.

## Phase 2 - Domain and Persistence Layer
1. Design and implement initial database schema:
- users
- rooms
- room_players
- game_rounds
- questions
- question_claims
- score_events
2. Implement repositories and domain entities.
3. Add transactional guards for question claiming and score updates.
4. Add seed scripts for local test data.

Deliverables:
- Migration files and repository interfaces.
- Domain model tests passing.

## Phase 3 - Real-time Room Management (MVP)
1. Implement room creation and join-by-code endpoints.
2. Implement WebSocket room channel and connection lifecycle handling.
3. Implement player presence and heartbeat mechanisms.
4. Broadcast room events (join/leave/status updates).

Deliverables:
- Multi-client room join flow working end to end.
- Stable WebSocket session handling under reconnect scenarios.

## Phase 4 - LLM Question Generation (MVP)
1. Define LLM provider interface and Factory Method initializer.
2. Implement first provider adapter and fallback/mock mode.
3. Build host action to request topic-based question batches.
4. Persist generated questions and expose claimable list to players.

Deliverables:
- Host can generate playable question sets by topic.
- Provider abstraction supports future providers without core rewrites.

## Phase 5 - First-Come Question Claim + Physical Scoring (MVP)
1. Implement atomic first-come claim operation.
2. Enforce one-winner claim semantics for race conditions.
3. Deliver full Q&A details only to claiming player.
4. Implement manual score submission and real-time leaderboard updates.

Deliverables:
- Claim race conditions handled correctly.
- Leaderboard updates broadcast in real time.

## Phase 6 - Validation, Hardening, and MVP Release
1. Add integration tests for room flow, claim flow, and scoring flow.
2. Add load checks for expected classroom concurrency.
3. Add error handling and reconnect recovery coverage.
4. Prepare deployment manifests and runtime config.
5. Perform MVP UAT checklist and release readiness review.

Deliverables:
- MVP release candidate.
- Test evidence and known limitation log.

## Phase 7 - Future Scaling Track (Remote/Livestream)
1. Implement player state machine (Available, Answering, Busy/Queued).
2. Implement remote question targeting and collision prevention.
3. Implement typed-answer submission UI and backend endpoints.
4. Implement LLM evaluator pipeline:
- input: question, ground-truth answer, user answer
- output: correctness, feedback, score
5. Add anti-abuse controls, rate limits, and moderation options.

Deliverables:
- Remote mode functional beta.
- Automated answer evaluation with explainable feedback.

## Cross-Cutting Workstreams
1. Security
- Secret management, auth/session strategy, audit logging.

2. Observability
- Structured logs, metrics dashboards, alert hooks.

3. Documentation
- API specs, WebSocket event contract docs, runbooks.

4. QA and Tooling
- Regression suite, smoke tests, and CI quality gates.

## Suggested Milestone Sequence
1. M0: Foundation Approved
2. M1: Skeleton + DB Ready
3. M2: Room and WebSocket Stable
4. M3: LLM Questioning and Claiming Complete
5. M4: MVP Release Candidate
6. M5: Remote Mode Beta
