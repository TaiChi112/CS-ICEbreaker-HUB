from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WsEvent(BaseModel):
    type: str
    payload: dict[str, object]
    occurred_at: datetime


class ClaimQuestionPayload(BaseModel):
    question_id: UUID
