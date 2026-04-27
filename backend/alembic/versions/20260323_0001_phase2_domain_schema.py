"""Phase 2 domain and persistence schema.

Revision ID: 20260323_0001
Revises:
Create Date: 2026-03-23 20:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260323_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


UUID = postgresql.UUID(as_uuid=True)
NOW_SQL = "now()"
ROOMS_ID_FK = "rooms.id"
ROOM_PLAYERS_ID_FK = "room_players.id"


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID, nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text(NOW_SQL), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "rooms",
        sa.Column("id", UUID, nullable=False),
        sa.Column("room_code", sa.String(length=12), nullable=False),
        sa.Column("host_user_id", UUID, nullable=False),
        sa.Column("status", sa.String(length=16), server_default="lobby", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text(NOW_SQL), nullable=False),
        sa.ForeignKeyConstraint(["host_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_code", name="uq_rooms_room_code"),
    )

    op.create_table(
        "room_players",
        sa.Column("id", UUID, nullable=False),
        sa.Column("room_id", UUID, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("role", sa.String(length=16), server_default="player", nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text(NOW_SQL), nullable=False),
        sa.ForeignKeyConstraint(["room_id"], [ROOMS_ID_FK], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_id", "user_id", name="uq_room_players_room_id_user_id"),
    )

    op.create_table(
        "game_rounds",
        sa.Column("id", UUID, nullable=False),
        sa.Column("room_id", UUID, nullable=False),
        sa.Column("topic", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text(NOW_SQL), nullable=False),
        sa.ForeignKeyConstraint(["room_id"], [ROOMS_ID_FK], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "questions",
        sa.Column("id", UUID, nullable=False),
        sa.Column("round_id", UUID, nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text(NOW_SQL), nullable=False),
        sa.ForeignKeyConstraint(["round_id"], ["game_rounds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "question_claims",
        sa.Column("id", UUID, nullable=False),
        sa.Column("question_id", UUID, nullable=False),
        sa.Column("selector_player_id", UUID, nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), server_default=sa.text(NOW_SQL), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["selector_player_id"], [ROOM_PLAYERS_ID_FK], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id", name="uq_question_claims_question_id"),
    )

    op.create_table(
        "score_events",
        sa.Column("id", UUID, nullable=False),
        sa.Column("room_id", UUID, nullable=False),
        sa.Column("scorer_player_id", UUID, nullable=False),
        sa.Column("target_player_id", UUID, nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text(NOW_SQL), nullable=False),
        sa.ForeignKeyConstraint(["room_id"], [ROOMS_ID_FK], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scorer_player_id"], [ROOM_PLAYERS_ID_FK], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["target_player_id"], [ROOM_PLAYERS_ID_FK], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("score_events")
    op.drop_table("question_claims")
    op.drop_table("questions")
    op.drop_table("game_rounds")
    op.drop_table("room_players")
    op.drop_table("rooms")
    op.drop_table("users")
