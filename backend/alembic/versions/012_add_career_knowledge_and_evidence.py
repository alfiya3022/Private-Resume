"""add career knowledge and evidence

Revision ID: 012_add_career_knowledge
Revises: 011_single_master_resume
Create Date: 2026-10-25 01:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "012_add_career_knowledge"
down_revision: Union[str, None] = "011_single_master_resume"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add source evidence and review status columns to candidate_skills if not exists
    op.add_column(
        "candidate_skills",
        sa.Column("source_evidence", sa.Text(), nullable=True),
    )
    op.add_column(
        "candidate_skills",
        sa.Column("review_status", sa.String(length=50), nullable=True, server_default="confirmed"),
    )

    # 2. Create career_knowledge_items table
    op.create_table(
        "career_knowledge_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("knowledge_type", sa.String(length=50), nullable=False, server_default="skill"),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=True),
        sa.Column("original_text", sa.String(length=255), nullable=False),
        sa.Column("normalized_term", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("aliases", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("source_evidence", sa.Text(), nullable=True),
        sa.Column("source_page", sa.Integer(), nullable=True),
        sa.Column("review_status", sa.String(length=50), nullable=False, server_default="extracted"),
        sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_career_knowledge_items_id"),
        "career_knowledge_items",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_career_knowledge_items_user_id"),
        "career_knowledge_items",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_career_knowledge_items_normalized_term"),
        "career_knowledge_items",
        ["normalized_term"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_career_knowledge_items_normalized_term"), table_name="career_knowledge_items")
    op.drop_index(op.f("ix_career_knowledge_items_user_id"), table_name="career_knowledge_items")
    op.drop_index(op.f("ix_career_knowledge_items_id"), table_name="career_knowledge_items")
    op.drop_table("career_knowledge_items")
    op.drop_column("candidate_skills", "review_status")
    op.drop_column("candidate_skills", "source_evidence")
