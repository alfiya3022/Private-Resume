"""master resume extraction pipeline and profile enhancements

Revision ID: 013_extraction_pipeline
Revises: 012_add_career_knowledge
Create Date: 2026-10-25 17:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "013_extraction_pipeline"
down_revision: Union[str, None] = "012_add_career_knowledge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add background parse tracking columns to master_resumes
    op.add_column(
        "master_resumes",
        sa.Column("parse_status", sa.String(length=50), nullable=False, server_default="complete"),
    )
    op.add_column(
        "master_resumes",
        sa.Column("parse_stage", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "master_resumes",
        sa.Column("parse_error", sa.Text(), nullable=True),
    )
    op.add_column(
        "master_resumes",
        sa.Column("parse_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "master_resumes",
        sa.Column("parse_finished_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 2. Update certifications table
    # Make issuer nullable as raw resume may not always declare an issuer
    op.alter_column(
        "certifications",
        "issuer",
        existing_type=sa.String(length=255),
        nullable=True,
    )
    op.add_column(
        "certifications",
        sa.Column("expiry_date", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "certifications",
        sa.Column("item_type", sa.String(length=50), nullable=False, server_default="certification"),
    )
    op.add_column(
        "certifications",
        sa.Column("status_note", sa.String(length=100), nullable=True),
    )

    # 3. Add technologies to experiences table
    op.add_column(
        "experiences",
        sa.Column("technologies", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("experiences", "technologies")
    op.drop_column("certifications", "status_note")
    op.drop_column("certifications", "item_type")
    op.drop_column("certifications", "expiry_date")
    op.alter_column(
        "certifications",
        "issuer",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.drop_column("master_resumes", "parse_finished_at")
    op.drop_column("master_resumes", "parse_started_at")
    op.drop_column("master_resumes", "parse_error")
    op.drop_column("master_resumes", "parse_stage")
    op.drop_column("master_resumes", "parse_status")
