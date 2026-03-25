from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import QuestionClaim
from app.domain.errors import AlreadyClaimedError
from app.domain.repositories import GameplayRepository


@dataclass(slots=True)
class ClaimQuestionUseCase:
    repository: GameplayRepository

    async def execute(self, *, question_id: UUID, selector_player_id: UUID) -> QuestionClaim:
        claim = await self.repository.claim_question_atomically(
            question_id=question_id,
            selector_player_id=selector_player_id,
        )
        if claim is None:
            raise AlreadyClaimedError("Question has already been claimed.")
        return claim
