from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import QuestionClaim, ScoreEvent
from app.domain.repositories import GameplayRepository
from app.infrastructure.db.mappers import to_domain_question_claim, to_domain_score_event
from app.infrastructure.db.models import QuestionClaimModel, RoomPlayerModel, ScoreEventModel


class SqlAlchemyGameplayRepository(GameplayRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def claim_question_atomically(
        self,
        *,
        question_id: UUID,
        selector_player_id: UUID,
    ) -> QuestionClaim | None:
        stmt = (
            insert(QuestionClaimModel)
            .values(question_id=question_id, selector_player_id=selector_player_id)
            .returning(QuestionClaimModel)
        )

        try:
            result = await self._session.execute(stmt)
            model = result.scalar_one()
            await self._session.commit()
            return to_domain_question_claim(model)
        except IntegrityError:
            await self._session.rollback()
            return None

    async def create_score_event(
        self,
        *,
        room_id: UUID,
        scorer_player_id: UUID,
        target_player_id: UUID,
        points: int,
        reason: str,
    ) -> ScoreEvent:
        membership_stmt = select(func.count()).select_from(RoomPlayerModel).where(
            RoomPlayerModel.room_id == room_id,
            RoomPlayerModel.id.in_([scorer_player_id, target_player_id]),
        )
        membership_count = await self._session.scalar(membership_stmt)
        if membership_count != 2:
            await self._session.rollback()
            raise ValueError("Scorer and target must both belong to the room.")

        stmt = (
            insert(ScoreEventModel)
            .values(
                room_id=room_id,
                scorer_player_id=scorer_player_id,
                target_player_id=target_player_id,
                points=points,
                reason=reason,
            )
            .returning(ScoreEventModel)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one()
        await self._session.commit()
        return to_domain_score_event(model)
