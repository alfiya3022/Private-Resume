"""add extracted_data to master_resumes

Revision ID: 010_add_extracted_data
Revises: 009_create_application_tables
Create Date: 2026-10-22 02:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "010_add_extracted_data"
down_revision: Union[str, None] = "009_create_application_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "master_resumes",
        sa.Column("extracted_data", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("master_resumes", "extracted_data")
