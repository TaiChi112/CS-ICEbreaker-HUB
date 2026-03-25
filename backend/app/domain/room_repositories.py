from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.room_views import LeaderboardEntry, RoomJoinResult, RoomSnapshot


class RoomRepository(Protocol):
    async def create_room(self, *, host_display_name: str) -> RoomJoinResult:
        """Create a room and host participant."""

    async def join_room(self, *, room_code: str, player_display_name: str) -> RoomJoinResult | None:
        """Join existing room by code. Returns None if room code does not exist."""

    async def get_room_snapshot(self, *, room_code: str) -> RoomSnapshot | None:
        """Return room state with participants, or None when room is missing."""

    async def get_leaderboard(self, *, room_id: UUID) -> list[LeaderboardEntry]:
        """Return room leaderboard sorted by score descending."""

    async def is_player_in_room(self, *, room_code: str, player_id: UUID) -> bool:
        """Validate that a room player belongs to the room code."""
