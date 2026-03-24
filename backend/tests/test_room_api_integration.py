from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.domain.entities import RoomStatus
from app.domain.room_views import LeaderboardEntry, RoomJoinResult, RoomParticipant, RoomSnapshot
from app.main import app


class FakeRoomRepository:
    async def create_room(self, *, host_display_name: str) -> RoomJoinResult:
        await asyncio.sleep(0)
        return RoomJoinResult(
            room_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            room_code="ABC123",
            player_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            user_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
            display_name=host_display_name,
            role="host",
        )

    async def join_room(self, *, room_code: str, player_display_name: str) -> RoomJoinResult | None:
        await asyncio.sleep(0)
        if room_code == "MISS00":
            return None

        return RoomJoinResult(
            room_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            room_code=room_code,
            player_id=uuid4(),
            user_id=uuid4(),
            display_name=player_display_name,
            role="player",
        )

    async def get_room_snapshot(self, *, room_code: str) -> RoomSnapshot | None:
        await asyncio.sleep(0)
        if room_code == "MISS00":
            return None

        return RoomSnapshot(
            room_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            room_code=room_code,
            status=RoomStatus.LOBBY,
            players=[
                RoomParticipant(
                    player_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                    user_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
                    display_name="Host Alice",
                    role="host",
                    joined_at=datetime.now(timezone.utc),
                )
            ],
        )

    async def get_leaderboard(self, *, room_id: UUID) -> list[LeaderboardEntry]:
        await asyncio.sleep(0)
        return [
            LeaderboardEntry(
                player_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                display_name="Host Alice",
                score=0,
            )
        ]


@asynccontextmanager
async def fake_session_context():
    yield object()


def test_create_room_endpoint(monkeypatch) -> None:
    import app.presentation.api.router as api_router_module

    monkeypatch.setattr(api_router_module, "SqlAlchemyRoomRepository", lambda _session: FakeRoomRepository())
    monkeypatch.setattr(api_router_module, "get_async_session", fake_session_context)

    client = TestClient(app)

    response = client.post("/api/rooms", json={"host_display_name": "Host Alice"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["room_code"] == "ABC123"
    assert payload["display_name"] == "Host Alice"
    assert payload["role"] == "host"


def test_join_room_endpoint_not_found(monkeypatch) -> None:
    import app.presentation.api.router as api_router_module

    monkeypatch.setattr(api_router_module, "SqlAlchemyRoomRepository", lambda _session: FakeRoomRepository())
    monkeypatch.setattr(api_router_module, "get_async_session", fake_session_context)

    client = TestClient(app)

    response = client.post(
        "/api/rooms/join",
        json={"room_code": "MISS00", "player_display_name": "Player Bob"},
    )

    assert response.status_code == 404
    assert "Room code was not found" in response.json()["detail"]


def test_get_room_state_endpoint(monkeypatch) -> None:
    import app.presentation.api.router as api_router_module

    monkeypatch.setattr(api_router_module, "SqlAlchemyRoomRepository", lambda _session: FakeRoomRepository())
    monkeypatch.setattr(api_router_module, "get_async_session", fake_session_context)

    client = TestClient(app)

    response = client.get("/api/rooms/abc123")

    assert response.status_code == 200
    payload = response.json()
    assert payload["room_code"] == "ABC123"
    assert payload["status"] == "lobby"
    assert len(payload["players"]) == 1
    assert payload["leaderboard"][0]["score"] == 0
