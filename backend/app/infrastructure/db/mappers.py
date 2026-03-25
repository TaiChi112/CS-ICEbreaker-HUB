from __future__ import annotations

from app.domain.entities import QuestionClaim, ScoreEvent
from app.infrastructure.db.models import QuestionClaimModel, ScoreEventModel


def to_domain_question_claim(model: QuestionClaimModel) -> QuestionClaim:
    return QuestionClaim(
        id=model.id,
        question_id=model.question_id,
        selector_player_id=model.selector_player_id,
        claimed_at=model.claimed_at,
    )


def to_domain_score_event(model: ScoreEventModel) -> ScoreEvent:
    return ScoreEvent(
        id=model.id,
        room_id=model.room_id,
        scorer_player_id=model.scorer_player_id,
        target_player_id=model.target_player_id,
        points=model.points,
        reason=model.reason,
        created_at=model.created_at,
    )
