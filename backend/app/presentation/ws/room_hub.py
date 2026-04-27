from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from fastapi import WebSocket


@dataclass(slots=True)
class RoomConnection:
    player_id: UUID
    display_name: str
    websocket: WebSocket
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RoomHub:
    def __init__(self) -> None:
        self._rooms: dict[str, dict[UUID, RoomConnection]] = defaultdict(dict)
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def connect(self, *, room_code: str, player_id: UUID, display_name: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._locks[room_code]:
            self._rooms[room_code][player_id] = RoomConnection(
                player_id=player_id,
                display_name=display_name,
                websocket=websocket,
            )

    async def disconnect(self, *, room_code: str, player_id: UUID) -> None:
        async with self._locks[room_code]:
            self._rooms[room_code].pop(player_id, None)
            if not self._rooms[room_code]:
                self._rooms.pop(room_code, None)
                self._locks.pop(room_code, None)

    def touch(self, *, room_code: str, player_id: UUID) -> None:
        connection = self._rooms.get(room_code, {}).get(player_id)
        if connection is not None:
            connection.last_seen = datetime.now(timezone.utc)

    async def send_to_player(self, *, room_code: str, player_id: UUID, message: dict[str, object]) -> None:
        connection = self._rooms.get(room_code, {}).get(player_id)
        if connection is None:
            return
        await connection.websocket.send_json(message)

    async def broadcast(self, *, room_code: str, message: dict[str, object]) -> None:
        room_connections = list(self._rooms.get(room_code, {}).values())
        if not room_connections:
            return

        stale: list[UUID] = []
        for connection in room_connections:
            try:
                await connection.websocket.send_json(message)
            except RuntimeError:
                stale.append(connection.player_id)

        for player_id in stale:
            await self.disconnect(room_code=room_code, player_id=player_id)


room_hub = RoomHub()
