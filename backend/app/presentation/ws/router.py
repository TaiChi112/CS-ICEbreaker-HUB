from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.application.use_cases.claim_question import ClaimQuestionUseCase
from app.core.config import get_settings
from app.domain.errors import AlreadyClaimedError
from app.infrastructure.db.repositories.gameplay_repository import SqlAlchemyGameplayRepository
from app.infrastructure.db.repositories.room_repository import SqlAlchemyRoomRepository
from app.infrastructure.db.session import get_async_session
from app.presentation.ws.room_hub import room_hub

ws_router = APIRouter()


@ws_router.websocket("/rooms/{room_code}")
async def room_channel(websocket: WebSocket, room_code: str, player_id: UUID, display_name: str) -> None:
    settings = get_settings()

    async with get_async_session() as session:
        room_repository = SqlAlchemyRoomRepository(session)
        in_room = await room_repository.is_player_in_room(room_code=room_code, player_id=player_id)

    if not in_room:
        await websocket.close(code=1008)
        return

    await room_hub.connect(
        room_code=room_code,
        player_id=player_id,
        display_name=display_name,
        websocket=websocket,
    )

    await room_hub.broadcast(
        room_code=room_code,
        message={
            "type": "player.joined",
            "payload": {"playerId": str(player_id), "displayName": display_name},
            "occurredAt": datetime.now(timezone.utc).isoformat(),
        },
    )

    try:
        while True:
            raw_message = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=settings.ws_ping_timeout_seconds,
            )
            message_type = str(raw_message.get("type", "")).strip()

            room_hub.touch(room_code=room_code, player_id=player_id)

            if message_type == "ping":
                await room_hub.send_to_player(
                    room_code=room_code,
                    player_id=player_id,
                    message={
                        "type": "pong",
                        "payload": {},
                        "occurredAt": datetime.now(timezone.utc).isoformat(),
                    },
                )
                continue

            if message_type == "question.claim":
                question_id = raw_message.get("payload", {}).get("questionId")
                if question_id is None:
                    await room_hub.send_to_player(
                        room_code=room_code,
                        player_id=player_id,
                        message={
                            "type": "question.claim_rejected",
                            "payload": {"reason": "questionId is required."},
                            "occurredAt": datetime.now(timezone.utc).isoformat(),
                        },
                    )
                    continue

                async with get_async_session() as session:
                    repository = SqlAlchemyGameplayRepository(session)
                    use_case = ClaimQuestionUseCase(repository=repository)
                    try:
                        claim = await use_case.execute(
                            question_id=UUID(str(question_id)),
                            selector_player_id=player_id,
                        )
                    except (AlreadyClaimedError, ValueError):
                        await room_hub.send_to_player(
                            room_code=room_code,
                            player_id=player_id,
                            message={
                                "type": "question.claim_rejected",
                                "payload": {"questionId": str(question_id), "reason": "Already claimed."},
                                "occurredAt": datetime.now(timezone.utc).isoformat(),
                            },
                        )
                        continue

                await room_hub.broadcast(
                    room_code=room_code,
                    message={
                        "type": "question.claimed",
                        "payload": {
                            "questionId": str(claim.question_id),
                            "selectorPlayerId": str(claim.selector_player_id),
                        },
                        "occurredAt": datetime.now(timezone.utc).isoformat(),
                    },
                )
    except TimeoutError:
        await websocket.close(code=1001)
    except WebSocketDisconnect:
        pass
    finally:
        await room_hub.disconnect(room_code=room_code, player_id=player_id)
        await room_hub.broadcast(
            room_code=room_code,
            message={
                "type": "player.left",
                "payload": {"playerId": str(player_id), "displayName": display_name},
                "occurredAt": datetime.now(timezone.utc).isoformat(),
            },
        )
