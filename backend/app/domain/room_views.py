from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities import RoomStatus


@dataclass(slots=True, frozen=True)
class RoomParticipant:
    player_id: UUID
    user_id: UUID
    display_name: str
    role: str
    joined_at: datetime


@dataclass(slots=True, frozen=True)
class RoomSnapshot:
    room_id: UUID
    room_code: str
    status: RoomStatus
    players: list[RoomParticipant]


@dataclass(slots=True, frozen=True)
class LeaderboardEntry:
    player_id: UUID
    display_name: str
    score: int


@dataclass(slots=True, frozen=True)
class RoomJoinResult:
    room_id: UUID
    room_code: str
    player_id: UUID
    user_id: UUID
    display_name: str
    role: str
