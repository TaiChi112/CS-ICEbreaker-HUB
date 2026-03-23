# Phase 1 Setup Guide

## 1. Prerequisites

- Python 3.12+
- Node.js 20+
- npm 10+
- Docker Desktop

## 2. Configure Environment

1. Copy .env.example to .env.
2. Update values as needed.

## 3. Start PostgreSQL

From repository root:

docker compose up -d

## 4. Start Backend

From repository root:

cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## 5. Run Backend Tests and Lint

From backend folder:

pytest
ruff check .
black --check .

## 6. Start Frontend

From repository root:

cd frontend
npm install
npm run dev

## 7. Run Frontend Tests and Lint

From frontend folder:

npm run test
npm run lint

## 8. Verify Setup

- API health endpoint: http://localhost:8000/api/health
- API DB health endpoint: http://localhost:8000/api/health/db
- Frontend app: http://localhost:3000
