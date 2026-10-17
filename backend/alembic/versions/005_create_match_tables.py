"""create match_analyses table

Revision ID: 005_create_match_tables
Revises: 004_create_analysis_tables
Create Date: 2026-10-17 23:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "005_create_match_tables"
down_revision: Union[str, None] = "004_create_analysis_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "match_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("estimated_match_score", sa.Integer(), nullable=False),
        sa.Column("matched_skills", sa.JSON(), nullable=False),
        sa.Column("weak_skills", sa.JSON(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("unsupported_claims", sa.JSON(), nullable=False),
        sa.Column("evidence_map", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_match_analyses_id"), "match_analyses", ["id"], unique=False)
    op.create_index(op.f("ix_match_analyses_job_id"), "match_analyses", ["job_id"], unique=True)
    op.create_index(op.f("ix_match_analyses_user_id"), "match_analyses", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_match_analyses_user_id"), table_name="match_analyses")
    op.drop_index(op.f("ix_match_analyses_job_id"), table_name="match_analyses")
    op.drop_index(op.f("ix_match_analyses_id"), table_name="match_analyses")
    op.drop_table("match_analyses")
