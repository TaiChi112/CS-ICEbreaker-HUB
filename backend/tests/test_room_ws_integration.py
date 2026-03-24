from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.domain.entities import QuestionClaim
from app.main import app


class FakeRoomRepository:
    async def is_player_in_room(self, *, room_code: str, player_id: UUID) -> bool:
        await asyncio.sleep(0)
        return room_code == "ABC123"


class FakeGameplayRepository:
    claimed_question_ids: set[UUID] = set()

    async def claim_question_atomically(
        self,
        *,
        question_id: UUID,
        selector_player_id: UUID,
    ) -> QuestionClaim | None:
        await asyncio.sleep(0)
        if question_id in self.claimed_question_ids:
            return None

        self.claimed_question_ids.add(question_id)
        return QuestionClaim(
            id=uuid4(),
            question_id=question_id,
            selector_player_id=selector_player_id,
            claimed_at=datetime.now(timezone.utc),
        )


@asynccontextmanager
async def fake_session_context():
    yield object()


def test_room_ws_first_claim_wins(monkeypatch) -> None:
    import app.presentation.ws.router as ws_router_module

    FakeGameplayRepository.claimed_question_ids.clear()
    monkeypatch.setattr(ws_router_module, "SqlAlchemyRoomRepository", lambda _session: FakeRoomRepository())
    monkeypatch.setattr(
        ws_router_module,
        "SqlAlchemyGameplayRepository",
        lambda _session: FakeGameplayRepository(),
    )
    monkeypatch.setattr(ws_router_module, "get_async_session", fake_session_context)

    client = TestClient(app)
    p1 = "11111111-1111-1111-1111-111111111111"
    p2 = "22222222-2222-2222-2222-222222222222"
    question_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    with client.websocket_connect(f"/ws/rooms/ABC123?player_id={p1}&display_name=Alice") as ws1:
        ws1.receive_json()

        with client.websocket_connect(f"/ws/rooms/ABC123?player_id={p2}&display_name=Bob") as ws2:
            ws1.receive_json()
            ws2.receive_json()

            ws1.send_json({"type": "question.claim", "payload": {"questionId": question_id}})
            event_for_p1 = ws1.receive_json()
            event_for_p2 = ws2.receive_json()

            assert event_for_p1["type"] == "question.claimed"
            assert event_for_p2["type"] == "question.claimed"

            ws2.send_json({"type": "question.claim", "payload": {"questionId": question_id}})
            rejected = ws2.receive_json()
            assert rejected["type"] == "question.claim_rejected"
