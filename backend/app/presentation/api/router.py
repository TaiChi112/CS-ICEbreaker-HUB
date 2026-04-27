from fastapi import APIRouter, HTTPException, status

from app.application.use_cases.create_room import CreateRoomUseCase
from app.application.use_cases.get_room_state import GetRoomStateUseCase
from app.application.use_cases.join_room import JoinRoomUseCase
from app.application.use_cases.generate_question_batch import GenerateQuestionBatchUseCase
from app.application.use_cases.list_claimable_questions import ListClaimableQuestionsUseCase
from app.core.config import get_settings
from app.domain.errors import ValidationError
from app.infrastructure.db.repositories.question_repository import SqlAlchemyQuestionRepository
from app.infrastructure.db.repositories.room_repository import SqlAlchemyRoomRepository
from app.infrastructure.db.session import get_async_session
from app.infrastructure.db.health import check_database_connection
from app.infrastructure.llm.factory import create_llm_provider
from app.presentation.api.schemas import (
    ClaimableQuestionsResponse,
    CreateRoomRequest,
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    JoinRoomRequest,
    RoomJoinResponse,
    RoomStateResponse,
)

api_router = APIRouter(tags=["system"])


@api_router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@api_router.get("/health/db")
async def health_db() -> dict[str, str]:
    is_connected = await check_database_connection()
    return {"database": "up" if is_connected else "down"}


@api_router.post("/rooms", status_code=status.HTTP_201_CREATED)
async def create_room(payload: CreateRoomRequest) -> RoomJoinResponse:
    async with get_async_session() as session:
        repository = SqlAlchemyRoomRepository(session)
        use_case = CreateRoomUseCase(repository=repository)
        result = await use_case.execute(host_display_name=payload.host_display_name)

    return RoomJoinResponse(
        room_id=result.room_id,
        room_code=result.room_code,
        player_id=result.player_id,
        user_id=result.user_id,
        display_name=result.display_name,
        role=result.role,
    )


@api_router.post("/rooms/join")
async def join_room(payload: JoinRoomRequest) -> RoomJoinResponse:
    async with get_async_session() as session:
        repository = SqlAlchemyRoomRepository(session)
        use_case = JoinRoomUseCase(repository=repository)
        try:
            result = await use_case.execute(
                room_code=payload.room_code.upper(),
                player_display_name=payload.player_display_name,
            )
        except ValidationError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return RoomJoinResponse(
        room_id=result.room_id,
        room_code=result.room_code,
        player_id=result.player_id,
        user_id=result.user_id,
        display_name=result.display_name,
        role=result.role,
    )


@api_router.get("/rooms/{room_code}")
async def get_room_state(room_code: str) -> RoomStateResponse:
    async with get_async_session() as session:
        repository = SqlAlchemyRoomRepository(session)
        use_case = GetRoomStateUseCase(repository=repository)
        try:
            room_state = await use_case.execute(room_code=room_code.upper())
        except ValidationError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return RoomStateResponse(
        room_id=room_state.snapshot.room_id,
        room_code=room_state.snapshot.room_code,
        status=room_state.snapshot.status.value,
        players=[
            {
                "player_id": player.player_id,
                "user_id": player.user_id,
                "display_name": player.display_name,
                "role": player.role,
                "joined_at": player.joined_at,
            }
            for player in room_state.snapshot.players
        ],
        leaderboard=[
            {
                "player_id": row.player_id,
                "display_name": row.display_name,
                "score": row.score,
            }
            for row in room_state.leaderboard
        ],
    )


@api_router.post("/rooms/{room_code}/questions/generate")
async def generate_questions(
    room_code: str,
    payload: GenerateQuestionsRequest,
) -> GenerateQuestionsResponse:
    settings = get_settings()
    llm_provider = create_llm_provider(settings)

    async with get_async_session() as session:
        repository = SqlAlchemyQuestionRepository(session)
        use_case = GenerateQuestionBatchUseCase(repository=repository, llm_provider=llm_provider)
        try:
            generated = await use_case.execute(
                room_code=room_code.upper(),
                host_player_id=payload.host_player_id,
                topic=payload.topic,
                batch_size=payload.batch_size,
            )
        except ValidationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return GenerateQuestionsResponse(
        room_id=generated.room_id,
        room_code=generated.room_code,
        round_id=generated.round_id,
        topic=generated.topic,
        question_count=len(generated.questions),
        questions=[
            {
                "question_id": item.question_id,
                "round_id": item.round_id,
                "prompt": item.prompt,
            }
            for item in generated.questions
        ],
    )


@api_router.get("/rooms/{room_code}/questions")
async def list_claimable_questions(room_code: str) -> ClaimableQuestionsResponse:
    async with get_async_session() as session:
        repository = SqlAlchemyQuestionRepository(session)
        use_case = ListClaimableQuestionsUseCase(repository=repository)
        questions = await use_case.execute(room_code=room_code.upper())

    return ClaimableQuestionsResponse(
        room_code=room_code.upper(),
        questions=[
            {
                "question_id": question.question_id,
                "round_id": question.round_id,
                "prompt": question.prompt,
            }
            for question in questions
        ],
    )
