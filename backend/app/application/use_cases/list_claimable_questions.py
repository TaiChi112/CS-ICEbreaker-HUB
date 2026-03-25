from __future__ import annotations

from dataclasses import dataclass

from app.domain.question_repositories import QuestionRepository
from app.domain.question_views import ClaimableQuestionItem


@dataclass(slots=True)
class ListClaimableQuestionsUseCase:
    repository: QuestionRepository

    async def execute(self, *, room_code: str) -> list[ClaimableQuestionItem]:
        return await self.repository.list_claimable_questions(room_code=room_code)
