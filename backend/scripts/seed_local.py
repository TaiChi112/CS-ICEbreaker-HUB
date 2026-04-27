from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path

from sqlalchemy import text

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.infrastructure.db.session import get_async_session


SEED_SQL_STATEMENTS = [
    """
    INSERT INTO users (id, display_name)
    VALUES
    (:host_user_id, 'Host Alice'),
    (:player_user_id, 'Player Bob')
    ON CONFLICT (id) DO NOTHING;
    """,
    """
    INSERT INTO rooms (id, room_code, host_user_id, status)
    VALUES
    (:room_id, 'CSHUB1', :host_user_id, 'lobby')
    ON CONFLICT (id) DO NOTHING;
    """,
    """
    INSERT INTO room_players (id, room_id, user_id, role)
    VALUES
    (:host_room_player_id, :room_id, :host_user_id, 'host'),
    (:player_room_player_id, :room_id, :player_user_id, 'player')
    ON CONFLICT (room_id, user_id) DO NOTHING;
    """,
    """
    INSERT INTO game_rounds (id, room_id, topic, status)
    VALUES
    (:round_id, :room_id, 'Data Structures', 'open')
    ON CONFLICT (id) DO NOTHING;
    """,
    """
    INSERT INTO questions (id, round_id, prompt, answer)
    VALUES
    (:question_id, :round_id, 'What is the time complexity of binary search?', 'O(log n)')
    ON CONFLICT (id) DO NOTHING;
    """,
]


async def seed() -> None:
    ids = {
        "host_user_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "player_user_id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
        "room_id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
        "host_room_player_id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
        "player_room_player_id": uuid.UUID("55555555-5555-5555-5555-555555555555"),
        "round_id": uuid.UUID("66666666-6666-6666-6666-666666666666"),
        "question_id": uuid.UUID("77777777-7777-7777-7777-777777777777"),
    }

    async with get_async_session() as session:
        for statement in SEED_SQL_STATEMENTS:
            await session.execute(text(statement), ids)
        await session.commit()

    print("Local seed data inserted successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
