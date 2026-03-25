from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class GeneratedQuestionItem:
    question_id: UUID
    round_id: UUID
    prompt: str


@dataclass(slots=True, frozen=True)
class GeneratedQuestionBatch:
    room_id: UUID
    room_code: str
    round_id: UUID
    topic: str
    questions: list[GeneratedQuestionItem]


@dataclass(slots=True, frozen=True)
class ClaimableQuestionItem:
    question_id: UUID
    round_id: UUID
    prompt: str
