"""create job_requirements table

Revision ID: 004_create_analysis_tables
Revises: 003_create_jobs_table
Create Date: 2026-10-17 23:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004_create_analysis_tables"
down_revision: Union[str, None] = "003_create_jobs_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_requirements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("required_skills", sa.JSON(), nullable=False),
        sa.Column("preferred_skills", sa.JSON(), nullable=False),
        sa.Column("languages", sa.JSON(), nullable=False),
        sa.Column("frameworks", sa.JSON(), nullable=False),
        sa.Column("databases", sa.JSON(), nullable=False),
        sa.Column("tools", sa.JSON(), nullable=False),
        sa.Column("cloud", sa.JSON(), nullable=False),
        sa.Column("responsibilities", sa.JSON(), nullable=False),
        sa.Column("qualifications", sa.JSON(), nullable=False),
        sa.Column("experience_years", sa.String(length=100), nullable=True),
        sa.Column("soft_skills", sa.JSON(), nullable=False),
        sa.Column("raw_analysis", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_requirements_id"), "job_requirements", ["id"], unique=False)
    op.create_index(op.f("ix_job_requirements_job_id"), "job_requirements", ["job_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_job_requirements_job_id"), table_name="job_requirements")
    op.drop_index(op.f("ix_job_requirements_id"), table_name="job_requirements")
    op.drop_table("job_requirements")
