from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import ScoreEvent
from app.domain.errors import ValidationError
from app.domain.repositories import GameplayRepository


@dataclass(slots=True)
class RecordScoreUseCase:
    repository: GameplayRepository

    async def execute(
        self,
        *,
        room_id: UUID,
        scorer_player_id: UUID,
        target_player_id: UUID,
        points: int,
        reason: str,
    ) -> ScoreEvent:
        if points < 0:
            raise ValidationError("Points must be non-negative.")
        if scorer_player_id == target_player_id:
            raise ValidationError("Scorer and target players must be different.")

        return await self.repository.create_score_event(
            room_id=room_id,
            scorer_player_id=scorer_player_id,
            target_player_id=target_player_id,
            points=points,
            reason=reason,
        )
