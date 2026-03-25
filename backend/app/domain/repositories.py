from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.entities import QuestionClaim, ScoreEvent


class GameplayRepository(Protocol):
    async def claim_question_atomically(
        self,
        *,
        question_id: UUID,
        selector_player_id: UUID,
    ) -> QuestionClaim | None:
        """Return None when the question is already claimed by another player."""

    async def create_score_event(
        self,
        *,
        room_id: UUID,
        scorer_player_id: UUID,
        target_player_id: UUID,
        points: int,
        reason: str,
    ) -> ScoreEvent:
        """Persist and return a score event."""
