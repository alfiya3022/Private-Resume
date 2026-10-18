"""create resume_artifacts table

Revision ID: 007_create_artifact_tables
Revises: 006_create_tailoring_tables
Create Date: 2026-10-18 15:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "007_create_artifact_tables"
down_revision: Union[str, None] = "006_create_tailoring_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resume_artifacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tailored_resume_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("artifact_type", sa.String(length=20), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("compilation_log", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tailored_resume_id"], ["tailored_resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resume_artifacts_id"), "resume_artifacts", ["id"], unique=False)
    op.create_index(op.f("ix_resume_artifacts_tailored_resume_id"), "resume_artifacts", ["tailored_resume_id"], unique=False)
    op.create_index(op.f("ix_resume_artifacts_user_id"), "resume_artifacts", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_resume_artifacts_user_id"), table_name="resume_artifacts")
    op.drop_index(op.f("ix_resume_artifacts_tailored_resume_id"), table_name="resume_artifacts")
    op.drop_index(op.f("ix_resume_artifacts_id"), table_name="resume_artifacts")
    op.drop_table("resume_artifacts")
