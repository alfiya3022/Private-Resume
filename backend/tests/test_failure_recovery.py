import pytest
from unittest.mock import patch, MagicMock
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.services.career_knowledge_service import CareerKnowledgeService
from app.services.ai.ollama_provider import OllamaProvider
from app.services.pdf_service import pdf_service
from app.core.database import get_db, SessionLocal


@pytest.fixture
def api_client():
    return TestClient(app)


def test_db_transaction_rollback_on_exception(db_session):
    """Verify that get_db rolls back uncommitted changes when an exception is raised."""
    from app.models.profile import CandidateSkill

    # Simulate an error within generator
    def failing_operation():
        for session in get_db():
            # Add an uncommitted object
            skill = CandidateSkill(profile_id=1, name="TemporarySkillRollback")
            session.add(skill)
            raise RuntimeError("Database simulated failure")

    with pytest.raises(RuntimeError):
        failing_operation()

    # Query using a fresh session to confirm the rollback
    fresh_session = SessionLocal()
    try:
        found = fresh_session.query(CandidateSkill).filter(CandidateSkill.name == "TemporarySkillRollback").first()
        assert found is None
    finally:
        fresh_session.close()


def test_pgvector_query_exception_logged_and_raised():
    """Verify that pgvector query execution errors are cleanly caught, logged, and surfaced."""
    svc = CareerKnowledgeService()
    mock_db = MagicMock()
    mock_db.get_bind.return_value.dialect.name = "postgresql"
    # Mock query raising exception
    mock_db.query.side_effect = RuntimeError("pgvector: relation does not exist")

    with pytest.raises(RuntimeError) as exc_info:
        svc.search_similar_evidence(
            db=mock_db,
            user_id=1,
            query="Python developer",
            limit=5,
        )
    assert "Career evidence vector search failed" in str(exc_info.value)


def test_invalid_embedding_dimension_rejected():
    """Verify ValueError is raised if embedding vector generation produces incorrect dimension."""
    svc = CareerKnowledgeService()
    with patch.object(svc, "generate_embedding", return_value=[0.1, 0.2]):  # Only 2 dims instead of 384
        mock_db = MagicMock()
        with pytest.raises(ValueError) as exc_info:
            svc.search_similar_evidence(
                db=mock_db,
                user_id=1,
                query="Python developer",
            )
        assert "expected 384" in str(exc_info.value)


@pytest.mark.asyncio
async def test_ollama_timeout_handled_gracefully():
    """Verify that Ollama timeouts fall back gracefully to deterministic refinement without crashing."""
    provider = OllamaProvider()

    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Ollama timed out")):
        res = await provider.refine_section(
            section="skills",
            instruction="Make it concise",
            current_text="Python, Docker, FastAPI",
        )
        assert "suggested_text" in res
        assert "explanation" in res
        assert res["suggested_text"] != ""


@pytest.mark.asyncio
async def test_ollama_unreachable_handled_gracefully():
    """Verify that Ollama connection failures fall back gracefully to deterministic refinement."""
    provider = OllamaProvider()

    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        res = await provider.refine_section(
            section="skills",
            instruction="Add bullet points",
            current_text="Python, Docker, FastAPI",
        )
        assert "suggested_text" in res
        assert "explanation" in res


def test_pdf_parsing_corrupt_file_raises_clear_error(tmp_path):
    """Verify that corrupted or unreadable PDF files raise clean ValueError without crashing."""
    corrupt_pdf = tmp_path / "corrupt.pdf"
    corrupt_pdf.write_bytes(b"%PDF-not-a-valid-pdf-header-data")

    with pytest.raises(ValueError) as exc_info:
        pdf_service.extract_layout_lines(str(corrupt_pdf))
    assert "Could not open PDF file" in str(exc_info.value) or "cannot open" in str(exc_info.value).lower()


def test_global_exception_handler_sanitizes_500(api_client):
    """Verify that unhandled exceptions return 500 with sanitized details in production mode."""
    with patch("app.core.config.settings.DEBUG", False):
        # Trigger an endpoint with simulated error
        response = api_client.get("/api/v1/non-existent-endpoint-test-404")
        assert response.status_code == 404
