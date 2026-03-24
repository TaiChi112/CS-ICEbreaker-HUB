from __future__ import annotations

import asyncio
from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest

from app.application.use_cases.generate_question_batch import GenerateQuestionBatchUseCase
from app.domain.errors import ValidationError
from app.domain.llm import GeneratedQuestion
from app.domain.question_views import GeneratedQuestionBatch, GeneratedQuestionItem


@dataclass
class FakeQuestionRepository:
    is_host: bool = True

    async def is_host_player_in_room(self, *, room_code: str, host_player_id: UUID) -> bool:
        await asyncio.sleep(0)
        return self.is_host

    async def create_round_with_questions(
        self,
        *,
        room_code: str,
        topic: str,
        questions: list[GeneratedQuestion],
    ) -> GeneratedQuestionBatch:
        await asyncio.sleep(0)
        return GeneratedQuestionBatch(
            room_id=uuid4(),
            room_code=room_code,
            round_id=uuid4(),
            topic=topic,
            questions=[
                GeneratedQuestionItem(question_id=uuid4(), round_id=uuid4(), prompt=q.prompt)
                for q in questions
            ],
        )

    async def list_claimable_questions(self, *, room_code: str):
        await asyncio.sleep(0)
        return []


class FakeLlmProvider:
    async def generate_question_batch(self, *, topic: str, batch_size: int) -> list[GeneratedQuestion]:
        await asyncio.sleep(0)
        return [
            GeneratedQuestion(prompt=f"{topic} q{idx + 1}", answer=f"a{idx + 1}")
            for idx in range(batch_size)
        ]


def test_generate_question_batch_use_case_validates_host() -> None:
    use_case = GenerateQuestionBatchUseCase(
        repository=FakeQuestionRepository(is_host=False),
        llm_provider=FakeLlmProvider(),
    )

    with pytest.raises(ValidationError):
        asyncio.run(
            use_case.execute(
                room_code="ABC123",
                host_player_id=uuid4(),
                topic="Operating Systems",
                batch_size=3,
            )
        )


def test_generate_question_batch_use_case_returns_batch() -> None:
    use_case = GenerateQuestionBatchUseCase(
        repository=FakeQuestionRepository(is_host=True),
        llm_provider=FakeLlmProvider(),
    )

    result = asyncio.run(
        use_case.execute(
            room_code="ABC123",
            host_player_id=uuid4(),
            topic="Operating Systems",
            batch_size=3,
        )
    )

    assert result.room_code == "ABC123"
    assert len(result.questions) == 3
