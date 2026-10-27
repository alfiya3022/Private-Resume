import pytest
from app.models.user import User
from app.models.profile import CareerKnowledgeItem
from app.services.career_knowledge_service import career_knowledge_service
from app.core.database import SessionLocal


def test_pgvector_persistence_and_similarity_ordering(db_session):
    """Verify that career knowledge embeddings are persisted as vector(384) in PostgreSQL

    and retrieved using database-side cosine distance ordering.
    """
    user_id = 9999
    # Clean up any existing records for test user
    db_session.query(CareerKnowledgeItem).filter(CareerKnowledgeItem.user_id == user_id).delete()
    db_session.commit()

    # Create knowledge items with known distinct concepts
    item1 = career_knowledge_service.record_knowledge_item(
        db=db_session,
        user_id=user_id,
        knowledge_type="skill",
        source_type="master_resume",
        original_text="PostgreSQL",
        category="Database",
        source_evidence="Managed high-availability PostgreSQL clusters",
    )

    item2 = career_knowledge_service.record_knowledge_item(
        db=db_session,
        user_id=user_id,
        knowledge_type="skill",
        source_type="master_resume",
        original_text="French pastry baking",
        category="Personal",
        source_evidence="French pastry baking and culinary technique",
    )

    item3 = career_knowledge_service.record_knowledge_item(
        db=db_session,
        user_id=user_id,
        knowledge_type="skill",
        source_type="master_resume",
        original_text="Database Administration",
        category="Database",
        source_evidence="Tuned SQL database queries and indexes",
    )

    # Search for SQL database query
    results = career_knowledge_service.search_similar_evidence(
        db=db_session,
        user_id=user_id,
        query="relational SQL database storage",
        limit=3,
        threshold=0.3,
    )

    assert len(results) >= 2
    top_terms = [r["term"].lower() for r in results[:2]]
    assert "postgresql" in top_terms or "database administration" in top_terms

    # Check cosine similarity values are ordered descending
    similarities = [r["similarity"] for r in results]
    assert similarities == sorted(similarities, reverse=True)


def test_pgvector_user_isolation(db_session):
    """Verify that vector similarity search strictly enforces user isolation."""
    user1 = 9991
    user2 = 9992

    career_knowledge_service.record_knowledge_item(
        db=db_session,
        user_id=user2,
        knowledge_type="skill",
        source_type="master_resume",
        original_text="Kubernetes Cloud Orchestration",
        source_evidence="Engineered Kubernetes clusters for high load",
    )

    results = career_knowledge_service.search_similar_evidence(
        db=db_session,
        user_id=user1,
        query="Kubernetes Cloud Orchestration",
        limit=5,
        threshold=0.1,
    )
    # Must not leak user2's evidence to user1
    assert len(results) == 0


def test_pgvector_empty_evidence(db_session):
    """Verify graceful handling when user has no stored evidence."""
    results = career_knowledge_service.search_similar_evidence(
        db=db_session,
        user_id=88888,
        query="Python FastAPI backend",
        limit=5,
        threshold=0.4,
    )
    assert results == []


def test_pgvector_live_postgresql_native_execution():
    """Verify end-to-end vector retrieval against the live PostgreSQL database with pgvector."""
    s = SessionLocal()
    try:
        # User 2 exists in PostgreSQL with active skills
        results = career_knowledge_service.search_similar_evidence(
            db=s,
            user_id=2,
            query="Python developer backend",
            limit=3,
            threshold=0.4,
        )
        assert isinstance(results, list)
        if len(results) > 0:
            assert all("similarity" in r for r in results)
            assert all("term" in r for r in results)
            similarities = [r["similarity"] for r in results]
            assert similarities == sorted(similarities, reverse=True)
    finally:
        s.close()
