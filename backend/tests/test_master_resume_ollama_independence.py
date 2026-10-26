import pytest
from unittest.mock import patch
from app.services.pdf_service import pdf_service
from app.services.ai.ollama_provider import ollama_provider


def test_master_resume_pipeline_independent_of_ollama(monkeypatch):
    """Verify Section 3.4: The master resume extraction pipeline does NOT depend on Ollama.

    Even if Ollama is completely offline, unreachable, or throwing connection exceptions,
    the pipeline completes successfully with structured data and valid status.
    """
    # Mock all Ollama provider methods to raise exceptions simulating offline Ollama
    async def mock_offline(*args, **kwargs):
        raise ConnectionRefusedError("Ollama is offline or unreachable on localhost:11434")

    monkeypatch.setattr(ollama_provider, "is_available", mock_offline)
    monkeypatch.setattr(ollama_provider, "analyze_job_description", mock_offline)
    monkeypatch.setattr(ollama_provider, "refine_section", mock_offline)

    # Verify that pdf_service extraction runs completely without raising any Ollama error
    test_pdf_path = "tests/fixtures/heldout/doc1_two_column_sidebar.pdf"
    raw_text = pdf_service.extract_text_from_pdf(test_pdf_path)
    extracted = pdf_service.extract_full_resume_data(test_pdf_path, raw_text=raw_text)

    # Assert structured data extracted successfully
    assert "personal_info" in extracted
    assert extracted["personal_info"].get("name") == "Devon Vance"
    assert "skills" in extracted
    assert len(extracted["skills"]) >= 10
    assert "projects" in extracted
    assert "experience" in extracted
    assert "education" in extracted
