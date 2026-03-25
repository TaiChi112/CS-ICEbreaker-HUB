from __future__ import annotations

from dataclasses import dataclass

from app.domain.errors import ValidationError
from app.domain.room_repositories import RoomRepository
from app.domain.room_views import LeaderboardEntry, RoomSnapshot


@dataclass(slots=True)
class RoomState:
    snapshot: RoomSnapshot
    leaderboard: list[LeaderboardEntry]


@dataclass(slots=True)
class GetRoomStateUseCase:
    repository: RoomRepository

    async def execute(self, *, room_code: str) -> RoomState:
        snapshot = await self.repository.get_room_snapshot(room_code=room_code)
        if snapshot is None:
            raise ValidationError("Room code was not found.")

        leaderboard = await self.repository.get_leaderboard(room_id=snapshot.room_id)
        return RoomState(snapshot=snapshot, leaderboard=leaderboard)
