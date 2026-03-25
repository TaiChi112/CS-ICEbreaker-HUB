from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.llm import GeneratedQuestion
from app.domain.question_views import ClaimableQuestionItem, GeneratedQuestionBatch


class QuestionRepository(Protocol):
    async def is_host_player_in_room(self, *, room_code: str, host_player_id: UUID) -> bool:
        """Validate room host authorization for generation."""

    async def create_round_with_questions(
        self,
        *,
        room_code: str,
        topic: str,
        questions: list[GeneratedQuestion],
    ) -> GeneratedQuestionBatch:
        """Persist a new open round and associated questions."""

    async def list_claimable_questions(self, *, room_code: str) -> list[ClaimableQuestionItem]:
        """Return unclaimed question prompts for active rounds in room."""
