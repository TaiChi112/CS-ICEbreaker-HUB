from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Select, func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import RoomStatus
from app.domain.room_repositories import RoomRepository
from app.domain.room_views import LeaderboardEntry, RoomJoinResult, RoomParticipant, RoomSnapshot
from app.infrastructure.db.models import RoomModel, RoomPlayerModel, ScoreEventModel, UserModel


def _new_room_code() -> str:
    return uuid.uuid4().hex[:6].upper()


class SqlAlchemyRoomRepository(RoomRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_room(self, *, host_display_name: str) -> RoomJoinResult:
        host_user_id = uuid.uuid4()
        room_id = uuid.uuid4()
        room_player_id = uuid.uuid4()

        host_user = UserModel(id=host_user_id, display_name=host_display_name)
        self._session.add(host_user)

        room: RoomModel | None = None
        for _ in range(8):
            candidate = RoomModel(
                id=room_id,
                room_code=_new_room_code(),
                host_user_id=host_user_id,
                status=RoomStatus.LOBBY.value,
            )
            self._session.add(candidate)
            try:
                await self._session.flush()
                room = candidate
                break
            except IntegrityError:
                await self._session.rollback()
                self._session.add(host_user)

        if room is None:
            raise ValueError("Could not generate unique room code.")

        room_player = RoomPlayerModel(
            id=room_player_id,
            room_id=room.id,
            user_id=host_user_id,
            role="host",
        )
        self._session.add(room_player)

        await self._session.commit()

        return RoomJoinResult(
            room_id=room.id,
            room_code=room.room_code,
            player_id=room_player.id,
            user_id=host_user_id,
            display_name=host_display_name,
            role="host",
        )

    async def join_room(self, *, room_code: str, player_display_name: str) -> RoomJoinResult | None:
        room_stmt: Select[tuple[RoomModel]] = select(RoomModel).where(RoomModel.room_code == room_code)
        room = await self._session.scalar(room_stmt)
        if room is None:
            return None

        user_id = uuid.uuid4()
        player_id = uuid.uuid4()

        self._session.add(UserModel(id=user_id, display_name=player_display_name))
        room_player = RoomPlayerModel(
            id=player_id,
            room_id=room.id,
            user_id=user_id,
            role="player",
        )
        self._session.add(room_player)
        await self._session.commit()

        return RoomJoinResult(
            room_id=room.id,
            room_code=room.room_code,
            player_id=player_id,
            user_id=user_id,
            display_name=player_display_name,
            role="player",
        )

    async def get_room_snapshot(self, *, room_code: str) -> RoomSnapshot | None:
        room_stmt = select(RoomModel).where(RoomModel.room_code == room_code)
        room = await self._session.scalar(room_stmt)
        if room is None:
            return None

        players_stmt = (
            select(RoomPlayerModel, UserModel)
            .join(UserModel, UserModel.id == RoomPlayerModel.user_id)
            .where(RoomPlayerModel.room_id == room.id)
            .order_by(RoomPlayerModel.joined_at.asc())
        )
        rows = await self._session.execute(players_stmt)

        players = [
            RoomParticipant(
                player_id=room_player.id,
                user_id=user.id,
                display_name=user.display_name,
                role=room_player.role,
                joined_at=room_player.joined_at
                if room_player.joined_at is not None
                else datetime.now(timezone.utc),
            )
            for room_player, user in rows
        ]

        return RoomSnapshot(
            room_id=room.id,
            room_code=room.room_code,
            status=RoomStatus(room.status),
            players=players,
        )

    async def get_leaderboard(self, *, room_id: uuid.UUID) -> list[LeaderboardEntry]:
        score_subquery = (
            select(
                ScoreEventModel.target_player_id.label("player_id"),
                func.coalesce(func.sum(ScoreEventModel.points), 0).label("score"),
            )
            .where(ScoreEventModel.room_id == room_id)
            .group_by(ScoreEventModel.target_player_id)
            .subquery()
        )

        stmt = (
            select(
                RoomPlayerModel.id,
                UserModel.display_name,
                func.coalesce(score_subquery.c.score, 0),
            )
            .join(UserModel, UserModel.id == RoomPlayerModel.user_id)
            .outerjoin(score_subquery, score_subquery.c.player_id == RoomPlayerModel.id)
            .where(RoomPlayerModel.room_id == room_id)
            .order_by(func.coalesce(score_subquery.c.score, 0).desc(), UserModel.display_name.asc())
        )

        rows = await self._session.execute(stmt)
        return [
            LeaderboardEntry(player_id=player_id, display_name=display_name, score=int(score))
            for player_id, display_name, score in rows
        ]

    async def is_player_in_room(self, *, room_code: str, player_id: uuid.UUID) -> bool:
        stmt = (
            select(func.count())
            .select_from(RoomPlayerModel)
            .join(RoomModel, RoomModel.id == RoomPlayerModel.room_id)
            .where(RoomModel.room_code == room_code, RoomPlayerModel.id == player_id)
        )
        count = await self._session.scalar(stmt)
        return bool(count and count > 0)
