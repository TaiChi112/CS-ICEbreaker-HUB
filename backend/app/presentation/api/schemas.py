from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateRoomRequest(BaseModel):
    host_display_name: str = Field(min_length=1, max_length=120)


class JoinRoomRequest(BaseModel):
    room_code: str = Field(min_length=4, max_length=12)
    player_display_name: str = Field(min_length=1, max_length=120)


class RoomJoinResponse(BaseModel):
    room_id: UUID
    room_code: str
    player_id: UUID
    user_id: UUID
    display_name: str
    role: str


class RoomPlayerResponse(BaseModel):
    player_id: UUID
    user_id: UUID
    display_name: str
    role: str
    joined_at: datetime


class LeaderboardEntryResponse(BaseModel):
    player_id: UUID
    display_name: str
    score: int


class RoomStateResponse(BaseModel):
    room_id: UUID
    room_code: str
    status: str
    players: list[RoomPlayerResponse]
    leaderboard: list[LeaderboardEntryResponse]


class GenerateQuestionsRequest(BaseModel):
    host_player_id: UUID
    topic: str = Field(min_length=1, max_length=160)
    batch_size: int = Field(default=8, ge=1, le=20)


class GeneratedQuestionResponse(BaseModel):
    question_id: UUID
    round_id: UUID
    prompt: str


class GenerateQuestionsResponse(BaseModel):
    room_id: UUID
    room_code: str
    round_id: UUID
    topic: str
    question_count: int
    questions: list[GeneratedQuestionResponse]


class ClaimableQuestionsResponse(BaseModel):
    room_code: str
    questions: list[GeneratedQuestionResponse]
