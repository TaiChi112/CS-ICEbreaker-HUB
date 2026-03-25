from __future__ import annotations

import json

import httpx

from app.domain.llm import GeneratedQuestion, LlmProvider


class OpenAiLlmProvider(LlmProvider):
    def __init__(self, *, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    async def generate_question_batch(self, *, topic: str, batch_size: int) -> list[GeneratedQuestion]:
        prompt = (
            "Generate a JSON array of trivia objects for computer science students. "
            "Each item must have keys 'prompt' and 'answer'. "
            f"Topic: {topic}. Count: {batch_size}."
        )

        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": "Return only strict JSON array with prompt and answer fields.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            body = response.json()

        content = body["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.lower().startswith("json"):
                content = content[4:].strip()

        data = json.loads(content)
        questions: list[GeneratedQuestion] = []
        for item in data:
            prompt_text = str(item.get("prompt", "")).strip()
            answer_text = str(item.get("answer", "")).strip()
            if prompt_text and answer_text:
                questions.append(GeneratedQuestion(prompt=prompt_text, answer=answer_text))

        if not questions:
            raise ValueError("OpenAI provider returned no valid questions.")

        return questions[:batch_size]
