"""create candidate profiles, skills, projects, experiences, educations, certifications, and master_resumes tables

Revision ID: 002_create_profile_tables
Revises: 001_create_users
Create Date: 2026-10-17 22:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_create_profile_tables"
down_revision: Union[str, None] = "001_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. candidate_profiles
    op.create_table(
        "candidate_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("headline", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("linkedin_url", sa.String(length=255), nullable=True),
        sa.Column("github_url", sa.String(length=255), nullable=True),
        sa.Column("portfolio_url", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_candidate_profiles_id"), "candidate_profiles", ["id"], unique=False)
    op.create_index(op.f("ix_candidate_profiles_user_id"), "candidate_profiles", ["user_id"], unique=True)

    # 2. candidate_skills
    op.create_table(
        "candidate_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("proficiency", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_candidate_skills_id"), "candidate_skills", ["id"], unique=False)
    op.create_index(op.f("ix_candidate_skills_name"), "candidate_skills", ["name"], unique=False)
    op.create_index(op.f("ix_candidate_skills_profile_id"), "candidate_skills", ["profile_id"], unique=False)

    # 3. projects
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("bullets", sa.JSON(), nullable=False),
        sa.Column("technologies", sa.JSON(), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.Column("start_date", sa.String(length=50), nullable=True),
        sa.Column("end_date", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)
    op.create_index(op.f("ix_projects_profile_id"), "projects", ["profile_id"], unique=False)

    # 4. experiences
    op.create_table(
        "experiences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("bullets", sa.JSON(), nullable=False),
        sa.Column("start_date", sa.String(length=50), nullable=True),
        sa.Column("end_date", sa.String(length=50), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_experiences_id"), "experiences", ["id"], unique=False)
    op.create_index(op.f("ix_experiences_profile_id"), "experiences", ["profile_id"], unique=False)

    # 5. educations
    op.create_table(
        "educations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("institution", sa.String(length=255), nullable=False),
        sa.Column("degree", sa.String(length=255), nullable=False),
        sa.Column("field_of_study", sa.String(length=255), nullable=True),
        sa.Column("grade", sa.String(length=50), nullable=True),
        sa.Column("start_date", sa.String(length=50), nullable=True),
        sa.Column("end_date", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_educations_id"), "educations", ["id"], unique=False)
    op.create_index(op.f("ix_educations_profile_id"), "educations", ["profile_id"], unique=False)

    # 6. certifications
    op.create_table(
        "certifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("issuer", sa.String(length=255), nullable=False),
        sa.Column("issue_date", sa.String(length=50), nullable=True),
        sa.Column("credential_url", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_certifications_id"), "certifications", ["id"], unique=False)
    op.create_index(op.f("ix_certifications_profile_id"), "certifications", ["profile_id"], unique=False)

    # 7. master_resumes
    op.create_table(
        "master_resumes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_master_resumes_id"), "master_resumes", ["id"], unique=False)
    op.create_index(op.f("ix_master_resumes_user_id"), "master_resumes", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("master_resumes")
    op.drop_table("certifications")
    op.drop_table("educations")
    op.drop_table("experiences")
    op.drop_table("projects")
    op.drop_table("candidate_skills")
    op.drop_table("candidate_profiles")
