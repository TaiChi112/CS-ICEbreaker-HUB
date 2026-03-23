# CS-Icebreaker Hub - Requirements

## 1. Project Overview

### 1.1 Project Name
CS-Icebreaker Hub (Real-time LLM Trivia Platform)

### 1.2 Vision
Create a real-time networking and assessment game for Computer Science students to bond, collaborate, and demonstrate domain knowledge through interactive trivia sessions.

### 1.3 Product Objective
Provide hosts and players with a low-latency, mobile-optimized experience where:
- Hosts create game rooms and launch topic-based question rounds.
- Players compete to select and deliver questions.
- Scores update in real time via WebSocket-driven events.

### 1.4 Primary Use Context
- In-person classroom or workshop icebreaker activities (MVP).
- Remote/livestream-compatible gameplay (future scaling).

## 2. Tech Stack

### 2.1 Recommended Stack
- Backend: FastAPI (Python) with high-performance WebSocket handling.
- Frontend: Next.js (React) with mobile-first responsive UI.
- Database: PostgreSQL.

### 2.2 Supporting Components
- ORM and migrations: SQLAlchemy + Alembic (or equivalent clean migration workflow).
- Real-time channel: Native WebSocket endpoint layer with room-scoped pub/sub events.
- LLM abstraction: Provider-agnostic adapter + factory initialization.
- Deployment baseline: Containerized local/dev runtime with environment-based configuration.

### 2.3 Why This Stack
- FastAPI offers rapid delivery while maintaining robust async I/O patterns for WebSockets.
- Next.js enables fast UI iteration and strong routing/data-fetching ergonomics.
- PostgreSQL provides reliable relational consistency for rooms, sessions, players, and scores.

## 3. Core Features

## 3.1 MVP (Physical Interaction Mode)
1. Room Management
- Host creates a room.
- Players join using a short room code.

2. LLM Question Generation
- Host submits a topic.
- Backend requests a batch of questions and answers from an LLM provider.

3. Real-time Selection
- Players only see question prompts (not answers).
- Question claiming is first-come, first-served with race-safe server arbitration.

4. Physical Q&A Workflow
- Selecting player receives full Q&A.
- Player asks another player in person.
- Selector submits manual score for the responder in the app.

5. Leaderboard
- Scores update and broadcast in real time.
- Players and host can view current rankings.

## 3.2 Future Scaling (Remote Play / Livestream Mode)
1. Remote Targeting
- A selected question can be delivered directly to a remote target player.

2. Collision Prevention
- Player states (for example Available, Answering) gate whether incoming questions are accepted, rejected, or queued.

3. Typed Answers
- Remote target submits typed answer via UI.

4. LLM Evaluation
- Backend sends original question, ground-truth answer, and user typed answer to evaluator model.
- System returns correctness judgment, feedback, and score assignment.

## 4. System Architecture

### 4.1 Architectural Style
- Clean Architecture with clear separation of concerns:
  - Presentation Layer: REST and WebSocket handlers.
  - Application Layer: Use cases and orchestration.
  - Domain Layer: Entities, business rules, and state transitions.
  - Infrastructure Layer: Database repositories, LLM providers, external integrations.

### 4.2 Real-time Event Model
- Room-scoped event bus semantics over WebSockets.
- Server authoritative state for:
  - Room lifecycle
  - Question pool and claim status
  - Player status
  - Scoreboard

### 4.3 Concurrency and State Control
- Enforce atomic question claim operations.
- Use explicit state machine or strict lock strategy for player status transitions.
- Prevent duplicate claims and invalid state transitions with transactional guards.

### 4.4 LLM Provider Design Pattern
- Apply Factory Method to initialize provider implementations (for example OpenAI, Anthropic, fallback mock provider).
- Define a common provider interface:
  - generate_question_batch(topic, constraints)
  - evaluate_answer(question, expected_answer, user_answer)

### 4.5 Data Model (Initial)
- users
- rooms
- room_players
- game_rounds
- questions
- question_claims
- answers (future)
- score_events

### 4.6 Security and Secrets
- All API keys and DSNs loaded from environment variables.
- No secrets committed to version control.
- Server-side validation on all score and state-changing actions.

## 5. Quality Standards and Non-Functional Requirements

### 5.1 Reliability
- Resilient WebSocket reconnect handling.
- Heartbeat/ping strategy for stale connection cleanup.

### 5.2 Performance
- Low-latency room updates under moderate classroom concurrency.
- Efficient fan-out broadcasting by room scope.

### 5.3 Maintainability
- Clear boundaries between domain logic and framework code.
- Testable application services and repositories.

### 5.4 Observability
- Structured logging with request and room correlation IDs.
- Basic metrics for active rooms, active sockets, and event throughput.

## 6. Coding Conventions

### 6.1 General
- Keep modules small and responsibility-focused.
- Favor explicit naming over abbreviations.
- Avoid hidden side effects in domain logic.

### 6.2 Backend Conventions
- Use type hints consistently.
- Keep HTTP/WebSocket handlers thin; move logic to use cases/services.
- Wrap external calls (LLM, database) behind interfaces.

### 6.3 Frontend Conventions
- Mobile-first responsive design.
- Separate UI components from state/data hooks.
- Centralize WebSocket event contracts and type definitions.

### 6.4 Data and Migration Conventions
- All schema changes via versioned migrations.
- Include rollback strategy notes for high-risk migrations.

### 6.5 Security Conventions
- Validate all user inputs and room actions server-side.
- Never log raw secrets or full tokens.
- Use environment variables for all credentials.

## 7. Out of Scope for Initial Setup
- Writing production application source code.
- Full CI/CD automation implementation.
- Multi-region deployment and advanced autoscaling.
