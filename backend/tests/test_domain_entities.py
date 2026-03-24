from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.domain.entities import PlayerRole, RoomPlayer


def test_room_player_entity_holds_expected_values() -> None:
    now = datetime.now(timezone.utc)
    room_player = RoomPlayer(
        id=uuid4(),
        room_id=uuid4(),
        user_id=uuid4(),
        role=PlayerRole.PLAYER,
        joined_at=now,
    )

    assert room_player.role is PlayerRole.PLAYER
    assert room_player.joined_at == now
