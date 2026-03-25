from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True, frozen=True)
class GeneratedQuestion:
    prompt: str
    answer: str


class LlmProvider(Protocol):
    async def generate_question_batch(self, *, topic: str, batch_size: int) -> list[GeneratedQuestion]:
        """Generate a list of prompt+answer items for gameplay."""
