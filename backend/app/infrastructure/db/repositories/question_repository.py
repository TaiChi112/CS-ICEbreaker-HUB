from __future__ import annotations

import uuid

from sqlalchemy import Select, exists, insert, outerjoin, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.llm import GeneratedQuestion
from app.domain.question_repositories import QuestionRepository
from app.domain.question_views import ClaimableQuestionItem, GeneratedQuestionBatch, GeneratedQuestionItem
from app.infrastructure.db.models import (
    GameRoundModel,
    QuestionClaimModel,
    QuestionModel,
    RoomModel,
    RoomPlayerModel,
)


class SqlAlchemyQuestionRepository(QuestionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def is_host_player_in_room(self, *, room_code: str, host_player_id: uuid.UUID) -> bool:
        stmt = (
            select(exists().where(
                RoomPlayerModel.id == host_player_id,
                RoomPlayerModel.role == "host",
                RoomModel.id == RoomPlayerModel.room_id,
                RoomModel.room_code == room_code,
            ))
        )
        result = await self._session.scalar(stmt)
        return bool(result)

    async def create_round_with_questions(
        self,
        *,
        room_code: str,
        topic: str,
        questions: list[GeneratedQuestion],
    ) -> GeneratedQuestionBatch:
        room_stmt: Select[tuple[RoomModel]] = select(RoomModel).where(RoomModel.room_code == room_code)
        room = await self._session.scalar(room_stmt)
        if room is None:
            raise ValueError("Room code was not found.")

        round_insert = (
            insert(GameRoundModel)
            .values(room_id=room.id, topic=topic, status="open")
            .returning(GameRoundModel)
        )
        round_model = (await self._session.execute(round_insert)).scalar_one()

        persisted_questions: list[GeneratedQuestionItem] = []
        for question in questions:
            q_insert = (
                insert(QuestionModel)
                .values(round_id=round_model.id, prompt=question.prompt, answer=question.answer)
                .returning(QuestionModel)
            )
            question_model = (await self._session.execute(q_insert)).scalar_one()
            persisted_questions.append(
                GeneratedQuestionItem(
                    question_id=question_model.id,
                    round_id=round_model.id,
                    prompt=question_model.prompt,
                )
            )

        await self._session.commit()

        return GeneratedQuestionBatch(
            room_id=room.id,
            room_code=room.room_code,
            round_id=round_model.id,
            topic=topic,
            questions=persisted_questions,
        )

    async def list_claimable_questions(self, *, room_code: str) -> list[ClaimableQuestionItem]:
        room_stmt = select(RoomModel.id).where(RoomModel.room_code == room_code)
        room_id = await self._session.scalar(room_stmt)
        if room_id is None:
            return []

        join_expr = outerjoin(QuestionModel, QuestionClaimModel, QuestionClaimModel.question_id == QuestionModel.id)
        stmt = (
            select(QuestionModel.id, QuestionModel.round_id, QuestionModel.prompt)
            .select_from(join_expr)
            .join(GameRoundModel, GameRoundModel.id == QuestionModel.round_id)
            .where(
                GameRoundModel.room_id == room_id,
                GameRoundModel.status == "open",
                QuestionClaimModel.id.is_(None),
            )
            .order_by(QuestionModel.created_at.asc())
        )

        rows = await self._session.execute(stmt)
        return [
            ClaimableQuestionItem(question_id=question_id, round_id=round_id, prompt=prompt)
            for question_id, round_id, prompt in rows
        ]
