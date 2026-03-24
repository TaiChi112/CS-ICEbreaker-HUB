from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from app.application.use_cases.claim_question import ClaimQuestionUseCase
from app.application.use_cases.record_score import RecordScoreUseCase
from app.domain.entities import QuestionClaim, ScoreEvent
from app.domain.errors import AlreadyClaimedError, ValidationError


@dataclass
class FakeGameplayRepository:
    claimed_questions: set[UUID]

    async def claim_question_atomically(
        self,
        *,
        question_id: UUID,
        selector_player_id: UUID,
    ) -> QuestionClaim | None:
        await asyncio.sleep(0)
        if question_id in self.claimed_questions:
            return None

        self.claimed_questions.add(question_id)
        return QuestionClaim(
            id=uuid4(),
            question_id=question_id,
            selector_player_id=selector_player_id,
            claimed_at=datetime.now(timezone.utc),
        )

    async def create_score_event(
        self,
        *,
        room_id: UUID,
        scorer_player_id: UUID,
        target_player_id: UUID,
        points: int,
        reason: str,
    ) -> ScoreEvent:
        await asyncio.sleep(0)
        return ScoreEvent(
            id=uuid4(),
            room_id=room_id,
            scorer_player_id=scorer_player_id,
            target_player_id=target_player_id,
            points=points,
            reason=reason,
            created_at=datetime.now(timezone.utc),
        )


def test_claim_question_use_case_raises_when_already_claimed() -> None:
    question_id = uuid4()
    repo = FakeGameplayRepository(claimed_questions={question_id})
    use_case = ClaimQuestionUseCase(repository=repo)

    with pytest.raises(AlreadyClaimedError):
        asyncio.run(use_case.execute(question_id=question_id, selector_player_id=uuid4()))


def test_claim_question_use_case_returns_claim_when_available() -> None:
    question_id = uuid4()
    selector_player_id = uuid4()
    repo = FakeGameplayRepository(claimed_questions=set())
    use_case = ClaimQuestionUseCase(repository=repo)

    claim = asyncio.run(
        use_case.execute(question_id=question_id, selector_player_id=selector_player_id)
    )

    assert claim.question_id == question_id
    assert claim.selector_player_id == selector_player_id


def test_record_score_use_case_validates_input() -> None:
    repo = FakeGameplayRepository(claimed_questions=set())
    use_case = RecordScoreUseCase(repository=repo)

    with pytest.raises(ValidationError):
        asyncio.run(
            use_case.execute(
                room_id=uuid4(),
                scorer_player_id=uuid4(),
                target_player_id=uuid4(),
                points=-1,
                reason="invalid",
            )
        )


def test_record_score_use_case_returns_event() -> None:
    room_id = uuid4()
    scorer = uuid4()
    target = uuid4()
    repo = FakeGameplayRepository(claimed_questions=set())
    use_case = RecordScoreUseCase(repository=repo)

    event = asyncio.run(
        use_case.execute(
            room_id=room_id,
            scorer_player_id=scorer,
            target_player_id=target,
            points=10,
            reason="Correct answer",
        )
    )

    assert event.room_id == room_id
    assert event.points == 10
