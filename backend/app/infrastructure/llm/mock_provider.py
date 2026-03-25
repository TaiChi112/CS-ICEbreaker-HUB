from __future__ import annotations

from app.domain.llm import GeneratedQuestion, LlmProvider


class MockLlmProvider(LlmProvider):
    async def generate_question_batch(self, *, topic: str, batch_size: int) -> list[GeneratedQuestion]:
        normalized_topic = topic.strip() or "Computer Science"
        return [
            GeneratedQuestion(
                prompt=f"[{normalized_topic}] Question {index + 1}: Explain concept {index + 1}.",
                answer=f"Reference answer for {normalized_topic} concept {index + 1}.",
            )
            for index in range(batch_size)
        ]
