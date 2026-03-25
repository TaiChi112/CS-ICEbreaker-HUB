from __future__ import annotations

from dataclasses import dataclass

from app.domain.room_repositories import RoomRepository
from app.domain.room_views import RoomJoinResult


@dataclass(slots=True)
class CreateRoomUseCase:
    repository: RoomRepository

    async def execute(self, *, host_display_name: str) -> RoomJoinResult:
        return await self.repository.create_room(host_display_name=host_display_name)
