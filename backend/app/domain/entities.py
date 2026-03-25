from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class RoomStatus(StrEnum):
    LOBBY = "lobby"
    ACTIVE = "active"
    COMPLETED = "completed"


class PlayerRole(StrEnum):
    HOST = "host"
    PLAYER = "player"


class RoundStatus(StrEnum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"


@dataclass(slots=True, frozen=True)
class User:
    id: UUID
    display_name: str
    created_at: datetime


@dataclass(slots=True, frozen=True)
class Room:
    id: UUID
    room_code: str
    host_user_id: UUID
    status: RoomStatus
    created_at: datetime


@dataclass(slots=True, frozen=True)
class RoomPlayer:
    id: UUID
    room_id: UUID
    user_id: UUID
    role: PlayerRole
    joined_at: datetime


@dataclass(slots=True, frozen=True)
class GameRound:
    id: UUID
    room_id: UUID
    topic: str
    status: RoundStatus
    created_at: datetime


@dataclass(slots=True, frozen=True)
class Question:
    id: UUID
    round_id: UUID
    prompt: str
    answer: str
    created_at: datetime


@dataclass(slots=True, frozen=True)
class QuestionClaim:
    id: UUID
    question_id: UUID
    selector_player_id: UUID
    claimed_at: datetime


@dataclass(slots=True, frozen=True)
class ScoreEvent:
    id: UUID
    room_id: UUID
    scorer_player_id: UUID
    target_player_id: UUID
    points: int
    reason: str
    created_at: datetime
