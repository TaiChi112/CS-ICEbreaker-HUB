>[!WARNING]
>Unpolished & Unorganized: You will likely encounter raw notes, inconsistent Markdown formatting, and incomplete setup guides. Formatting cleanup is performed in batches rather than continuously.

>[!CAUTION]
>Breaking Changes: Expect frequent refactors that may break existing functionality without notice. Do not rely on this project for production-critical tasks until a stable release (v1.0.0) is tagged.

>[!NOTE]
>Project Context: This repository is part of my personal R&D and academic journey as an Agentic Software Engineer. It serves as a sandbox for exploring new architectures and performance-oriented languages.

>[!TIP]
>How to Navigate: Since the documentation might lag behind, the most reliable way to understand the current logic is to check the recent commit history or explore the /src directory directly.

>[!IMPORTANT]
>Documentation Mismatch: I am prioritizing "Vibe Coding" and rapid feature iteration over documentation updates. Most of the README content below is stale or reflects an older architectural version.

# CS-Icebreaker Hub

CS-Icebreaker Hub is a real-time LLM trivia platform designed for Computer Science networking, engagement, and lightweight knowledge assessment.

The current implementation uses:

- FastAPI for backend REST and WebSocket services
- Next.js App Router for host/player frontend workflows
- PostgreSQL for authoritative room, question, and scoring state
- Provider-based LLM integration for question generation

## Quick Start

### Prerequisites

- Python 3.12+
- Bun 1.3+ (or Node.js 20+)
- Docker Desktop

### 1) Environment Configuration

Use the detailed setup guide:

- [docs/ENVIRONMENT_SETUP.md](docs/ENVIRONMENT_SETUP.md)

Create local environment file from project root:

```bash
cp .env.example .env
```

### 2) Start PostgreSQL

```bash
docker compose up -d
```

### 3) Start Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements-dev.txt
.venv/Scripts/alembic.exe upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API docs:

- http://localhost:8000/api/docs

### 4) Start Frontend

```bash
cd frontend
bun install
bun run dev
```

### 5) Run Tests

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
bun test
```

### 6) Local Endpoints

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- API Health: http://localhost:8000/api/health
- DB Health: http://localhost:8000/api/health/db

## Documentation Directory

- [Environment Setup Guide](docs/ENVIRONMENT_SETUP.md)
- [SDLC 01: Requirements and Analysis](docs/sdlc/01_Requirements_and_Analysis.md)
- [SDLC 02: System Design](docs/sdlc/02_System_Design.md)
- [SDLC 03: Implementation](docs/sdlc/03_Implementation.md)
- [SDLC 04: Testing and QA](docs/sdlc/04_Testing_and_QA.md)
- [SDLC 05: Deployment and DevOps](docs/sdlc/05_Deployment_and_DevOps.md)
- [SDLC 06: Maintenance and Evolution](docs/sdlc/06_Maintenance_and_Evolution.md)

## Repository Structure

- [backend](backend)
- [frontend](frontend)
- [shared/contracts](shared/contracts)
- [docs](docs)
