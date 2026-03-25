from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.errors import ValidationError
from app.domain.llm import LlmProvider
from app.domain.question_repositories import QuestionRepository
from app.domain.question_views import GeneratedQuestionBatch


@dataclass(slots=True)
class GenerateQuestionBatchUseCase:
    repository: QuestionRepository
    llm_provider: LlmProvider

    async def execute(
        self,
        *,
        room_code: str,
        host_player_id: UUID,
        topic: str,
        batch_size: int,
    ) -> GeneratedQuestionBatch:
        normalized_topic = topic.strip()
        if not normalized_topic:
            raise ValidationError("Topic is required.")
        if batch_size < 1 or batch_size > 20:
            raise ValidationError("batch_size must be between 1 and 20.")

        is_host = await self.repository.is_host_player_in_room(
            room_code=room_code,
            host_player_id=host_player_id,
        )
        if not is_host:
            raise ValidationError("Only the room host can generate question batches.")

        generated_questions = await self.llm_provider.generate_question_batch(
            topic=normalized_topic,
            batch_size=batch_size,
        )
        if not generated_questions:
            raise ValidationError("LLM returned no questions.")

        return await self.repository.create_round_with_questions(
            room_code=room_code,
            topic=normalized_topic,
            questions=generated_questions,
        )
