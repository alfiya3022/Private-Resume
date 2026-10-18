"""create resume_validations table

Revision ID: 008_create_validation_tables
Revises: 007_create_artifact_tables
Create Date: 2026-10-18 16:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "008_create_validation_tables"
down_revision: Union[str, None] = "007_create_artifact_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resume_validations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tailored_resume_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("overall_status", sa.String(length=20), nullable=False, server_default="PASS"),
        sa.Column("score", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("checks", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tailored_resume_id"], ["tailored_resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resume_validations_id"), "resume_validations", ["id"], unique=False)
    op.create_index(op.f("ix_resume_validations_tailored_resume_id"), "resume_validations", ["tailored_resume_id"], unique=False)
    op.create_index(op.f("ix_resume_validations_user_id"), "resume_validations", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_resume_validations_user_id"), table_name="resume_validations")
    op.drop_index(op.f("ix_resume_validations_tailored_resume_id"), table_name="resume_validations")
    op.drop_index(op.f("ix_resume_validations_id"), table_name="resume_validations")
    op.drop_table("resume_validations")
