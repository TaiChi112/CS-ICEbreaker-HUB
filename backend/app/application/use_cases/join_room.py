from __future__ import annotations

from dataclasses import dataclass

from app.domain.errors import ValidationError
from app.domain.room_repositories import RoomRepository
from app.domain.room_views import RoomJoinResult


@dataclass(slots=True)
class JoinRoomUseCase:
    repository: RoomRepository

    async def execute(self, *, room_code: str, player_display_name: str) -> RoomJoinResult:
        result = await self.repository.join_room(
            room_code=room_code,
            player_display_name=player_display_name,
        )
        if result is None:
            raise ValidationError("Room code was not found.")
        return result
