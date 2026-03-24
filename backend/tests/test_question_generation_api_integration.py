from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi.testclient import TestClient

from app.domain.llm import GeneratedQuestion
from app.domain.question_views import ClaimableQuestionItem, GeneratedQuestionBatch, GeneratedQuestionItem
from app.main import app


class FakeQuestionRepository:
    async def is_host_player_in_room(self, *, room_code: str, host_player_id: UUID) -> bool:
        await asyncio.sleep(0)
        return room_code == "ABC123"

    async def create_round_with_questions(self, *, room_code: str, topic: str, questions: list[GeneratedQuestion]) -> GeneratedQuestionBatch:
        await asyncio.sleep(0)
        return GeneratedQuestionBatch(
            room_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            room_code=room_code,
            round_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            topic=topic,
            questions=[
                GeneratedQuestionItem(
                    question_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
                    round_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                    prompt=questions[0].prompt,
                )
            ],
        )

    async def list_claimable_questions(self, *, room_code: str) -> list[ClaimableQuestionItem]:
        await asyncio.sleep(0)
        return [
            ClaimableQuestionItem(
                question_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
                round_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                prompt="What is TCP?",
            )
        ]


class FakeLlmProvider:
    async def generate_question_batch(self, *, topic: str, batch_size: int) -> list[GeneratedQuestion]:
        await asyncio.sleep(0)
        return [GeneratedQuestion(prompt=f"{topic} question", answer="sample answer")]


@asynccontextmanager
async def fake_session_context():
    yield object()


def test_generate_questions_endpoint(monkeypatch) -> None:
    import app.presentation.api.router as api_router_module

    monkeypatch.setattr(api_router_module, "SqlAlchemyQuestionRepository", lambda _session: FakeQuestionRepository())
    monkeypatch.setattr(api_router_module, "create_llm_provider", lambda _settings: FakeLlmProvider())
    monkeypatch.setattr(api_router_module, "get_async_session", fake_session_context)

    client = TestClient(app)
    response = client.post(
        "/api/rooms/ABC123/questions/generate",
        json={
            "host_player_id": "11111111-1111-1111-1111-111111111111",
            "topic": "Computer Networks",
            "batch_size": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["room_code"] == "ABC123"
    assert payload["topic"] == "Computer Networks"
    assert payload["question_count"] == 1


def test_list_claimable_questions_endpoint(monkeypatch) -> None:
    import app.presentation.api.router as api_router_module

    monkeypatch.setattr(api_router_module, "SqlAlchemyQuestionRepository", lambda _session: FakeQuestionRepository())
    monkeypatch.setattr(api_router_module, "get_async_session", fake_session_context)

    client = TestClient(app)
    response = client.get("/api/rooms/ABC123/questions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["room_code"] == "ABC123"
    assert len(payload["questions"]) == 1
