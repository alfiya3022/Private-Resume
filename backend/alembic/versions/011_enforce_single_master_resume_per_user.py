"""enforce single master resume per user

Revision ID: 011_single_master_resume
Revises: 010_add_extracted_data
Create Date: 2026-10-22 21:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "011_single_master_resume"
down_revision: Union[str, None] = "010_add_extracted_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Safely deduplicate if any user has multiple master resumes, keeping the latest one
    conn = op.get_bind()
    conn.execute(sa.text("""
        DELETE FROM master_resumes
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM master_resumes
            GROUP BY user_id
        )
    """))

    # 2. Add unique constraint on user_id
    op.create_unique_constraint(
        "uq_master_resumes_user_id",
        "master_resumes",
        ["user_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_master_resumes_user_id", "master_resumes", type_="unique")
