"""add onboarding_completed to users

Revision ID: 014_add_onboarding_completed
Revises: 013_extraction_pipeline
Create Date: 2026-10-26 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "014_add_onboarding_completed"
down_revision: Union[str, None] = "013_extraction_pipeline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # Mark existing users with active master resumes or profiles as already onboarded
    op.execute(
        """
        UPDATE users
        SET onboarding_completed = TRUE
        WHERE id IN (
            SELECT user_id FROM master_resumes
            UNION
            SELECT user_id FROM candidate_profiles WHERE headline IS NOT NULL OR summary IS NOT NULL
        )
        """
    )


def downgrade() -> None:
    op.drop_column("users", "onboarding_completed")
