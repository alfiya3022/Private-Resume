"""enable pgvector and vector column

Revision ID: 015_enable_pgvector
Revises: 014_add_onboarding_completed
Create Date: 2026-10-27 01:45:00.000000

"""
from typing import Sequence, Union
import json
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


revision: str = "015_enable_pgvector"
down_revision: Union[str, None] = "014_add_onboarding_completed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Add temporary vector(384) column
    op.execute("ALTER TABLE career_knowledge_items ADD COLUMN embedding_vec vector(384);")

    # 3. Populate embedding_vec from existing JSON embedding using Python batched iteration to ensure clean vector formatting
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        rows = session.execute(
            sa.text("SELECT id, embedding FROM career_knowledge_items WHERE embedding IS NOT NULL")
        ).fetchall()

        for row in rows:
            raw_emb = row[1]
            if raw_emb is None:
                continue
            if isinstance(raw_emb, str):
                try:
                    vec_list = json.loads(raw_emb)
                except Exception:
                    continue
            else:
                vec_list = raw_emb

            if isinstance(vec_list, list) and len(vec_list) == 384:
                # Format as vector literal: '[0.1, 0.2, ...]'
                vec_str = "[" + ",".join(str(float(x)) for x in vec_list) + "]"
                session.execute(
                    sa.text("UPDATE career_knowledge_items SET embedding_vec = :vec WHERE id = :id"),
                    {"vec": vec_str, "id": row[0]},
                )
        session.commit()
    except Exception:
        session.rollback()
        raise

    # 4. Drop old JSON column and rename embedding_vec to embedding
    op.drop_column("career_knowledge_items", "embedding")
    op.execute("ALTER TABLE career_knowledge_items RENAME COLUMN embedding_vec TO embedding;")

    # 5. Create HNSW index for cosine distance similarity
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_career_knowledge_items_embedding_hnsw
        ON career_knowledge_items USING hnsw (embedding vector_cosine_ops);
        """
    )


def downgrade() -> None:
    # 1. Drop HNSW index
    op.execute("DROP INDEX IF EXISTS ix_career_knowledge_items_embedding_hnsw;")

    # 2. Add JSON column
    op.execute("ALTER TABLE career_knowledge_items ADD COLUMN embedding_json JSON;")

    # 3. Convert vector(384) back to JSON array
    op.execute(
        """
        UPDATE career_knowledge_items
        SET embedding_json = (
            CASE
                WHEN embedding IS NOT NULL
                THEN embedding::text::json
                ELSE NULL
            END
        );
        """
    )

    # 4. Drop vector column and rename JSON column back
    op.drop_column("career_knowledge_items", "embedding")
    op.execute("ALTER TABLE career_knowledge_items RENAME COLUMN embedding_json TO embedding;")
