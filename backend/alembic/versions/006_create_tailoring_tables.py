"""create tailored_resumes table

Revision ID: 006_create_tailoring_tables
Revises: 005_create_match_tables
Create Date: 2026-10-18 00:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "006_create_tailoring_tables"
down_revision: Union[str, None] = "005_create_match_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tailored_resumes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("parent_version_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("target_role", sa.String(length=150), nullable=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_version_id"], ["tailored_resumes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tailored_resumes_id"), "tailored_resumes", ["id"], unique=False)
    op.create_index(op.f("ix_tailored_resumes_job_id"), "tailored_resumes", ["job_id"], unique=False)
    op.create_index(op.f("ix_tailored_resumes_user_id"), "tailored_resumes", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tailored_resumes_user_id"), table_name="tailored_resumes")
    op.drop_index(op.f("ix_tailored_resumes_job_id"), table_name="tailored_resumes")
    op.drop_index(op.f("ix_tailored_resumes_id"), table_name="tailored_resumes")
    op.drop_table("tailored_resumes")
