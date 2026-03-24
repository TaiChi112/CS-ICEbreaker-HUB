# 04 Testing and QA

## 1. Document Purpose

This document defines the testing strategy and quality assurance posture for CS-Icebreaker Hub.
It includes current audit findings and technical debt items to support structured remediation.

## 2. Test Strategy

### 2.1 Unit Testing

Objective:

- Validate isolated business logic and utility behavior with deterministic inputs.

Scope:

- Domain entities, validation rules, and error handling
- Application use cases with mocked repository/provider dependencies
- Adapter-level utility logic where deterministic behavior is expected

Expected outcome:

- Fast feedback for regressions in core business rules
- High confidence in invariant enforcement independent of transport and DB layers

### 2.2 Integration Testing

Objective:

- Validate interaction across layers and major runtime boundaries.

Scope:

- API route to use-case to repository paths
- Persistence behavior against relational constraints
- WebSocket claim flow and room event propagation semantics
- LLM provider factory behavior under configured and fallback modes

Expected outcome:

- Confidence that system components behave correctly when composed
- Early detection of schema, serialization, and orchestration regressions

### 2.3 End-to-End (E2E) Testing

Objective:

- Validate complete user workflows from frontend actions to backend effects.

Recommended scope:

- Host creates room, player joins, host generates questions, players claim question
- Score submission and leaderboard update visibility
- Network interruption and reconnection user experience

Expected outcome:

- Product-level confidence for release readiness
- Detection of UX and protocol mismatches that unit/integration tests cannot expose

## 3. QA Audit Summary

A focused technical audit has already been completed across:

- Frontend WebSocket client behavior
- Backend WebSocket routing and room hub logic
- Use-case and repository boundary behavior
- Shared contract consistency between backend and frontend

Current QA posture:

- MVP is operational.
- High-impact reliability and security hardening work remains open.
- Remediation is tracked in the technical debt backlog below.

## 4. Technical Debt (Help Wanted)

Contributors are encouraged to select one backlog item and submit a focused PR with tests and contract updates.

### 4.1 Backend

- [ ] [Critical] Enforce room-bound ownership checks for question claims before writing to `question_claims`.
- [ ] [High] Eliminate WebSocket identity spoofing by making server-side identity authoritative (ignore client-provided display names for trust decisions).
- [ ] [High] Standardize room code normalization for WebSocket routes and membership checks.
- [ ] [High] Harden WebSocket send/broadcast paths with broader transport exception handling and safe connection cleanup.
- [ ] [Medium] Emit explicit error responses for unsupported/unknown WebSocket message types.
- [ ] [Medium] Add structured disconnect reason payloads so clients can distinguish timeout, policy, and server-fault closures.
- [ ] [Medium] Add rate limiting and anti-spam controls for `question.claim` attempts.
- [ ] [Low] Use `last_seen` for stale connection pruning and room-presence observability metrics.

### 4.2 Frontend

- [ ] [High] Implement automatic WebSocket reconnection with bounded retry policy and exponential backoff.
- [ ] [High] Add cancellation/order guards for concurrent room refresh requests to prevent stale-state overwrites.
- [ ] [Medium] Add explicit loading states for initial room fetch and async actions (including question generation).
- [ ] [Medium] Preserve structured backend error details in UI feedback instead of generic fallback errors.
- [ ] [Medium] Add pending/disabled state for claim actions to prevent duplicate in-flight submissions.
- [ ] [Low] Replace placeholder reveal answers with authoritative backend-provided values.
- [ ] [Medium] Add guided recovery UX when room context parameters are missing or invalid.

### 4.3 Shared Contracts

- [ ] [High] Unify WebSocket event envelope naming across schemas and runtime payloads.
- [ ] [High] Tighten WebSocket payload schema constraints to detect field drift and enforce compatibility.
- [ ] [Medium] Standardize API/WS casing strategy and document mapping rules to reduce integration errors.

## 5. Quality Gates (Recommended)

- Pull requests should pass backend and frontend automated tests.
- New API and event contract changes should include schema updates and compatibility checks.
- High-risk changes in websocket arbitration and scoring logic should include integration tests.
