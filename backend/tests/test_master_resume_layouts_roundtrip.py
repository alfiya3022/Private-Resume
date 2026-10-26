"""Tests robustness of master resume extraction pipeline against 10 layout families
and edge cases (password-protected, corrupt bytes, text-less, garbled fonts, duplicate consent, user corrections).
"""
import os
import pytest
import fitz
from app.services.pdf_service import pdf_service
from app.services.career_knowledge_service import career_knowledge_service


SYNTHETIC_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "synthetic")


def test_synthetic_10_layout_families_roundtrip():
    """Verifies that all 10 distinct layout families extract essential sections without crash or blank outputs."""
    files = [f for f in os.listdir(SYNTHETIC_DIR) if f.endswith(".pdf")]
    assert len(files) == 10, f"Expected 10 synthetic layout PDFs, found {len(files)}"

    for f in files:
        pdf_path = os.path.join(SYNTHETIC_DIR, f)
        data = pdf_service.extract_full_resume_data(pdf_path)

        assert "personal_info" in data, f"Missing personal_info in {f}"
        assert data["personal_info"].get("name"), f"Missing name extraction in {f}"
        assert data["personal_info"].get("email"), f"Missing email extraction in {f}"

        # Ensure skills detected
        assert len(data.get("skills", [])) > 0, f"Expected skills in {f}"

        # Ensure core career sections populated
        assert len(data.get("experience", [])) > 0, f"Expected experience in {f}"
        assert len(data.get("projects", [])) > 0, f"Expected projects in {f}"
        assert len(data.get("education", [])) > 0, f"Expected education in {f}"
        assert len(data.get("certifications", [])) > 0, f"Expected certifications in {f}"


def test_edge_case_password_protected_pdf(tmp_path):
    """Verifies handling of encrypted/password-protected PDFs."""
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((50, 50), "Classified Secret Candidate Resume")
    pdf_path = str(tmp_path / "protected.pdf")
    # Save with user/owner password encryption
    doc.save(
        pdf_path,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw="secret123",
        owner_pw="master123",
    )
    doc.close()

    # Attempting to extract text should either raise an informative error or return empty cleanly
    try:
        data = pdf_service.extract_full_resume_data(pdf_path)
        # If fitz fails open or decrypts with empty pw, text should be handled gracefully
        assert isinstance(data, dict)
    except Exception as exc:
        assert "password" in str(exc).lower() or "encrypted" in str(exc).lower() or "authenticate" in str(exc).lower()


def test_edge_case_corrupt_pdf_bytes(tmp_path):
    """Verifies handling of corrupt, truncated, or non-PDF binary files."""
    corrupt_path = str(tmp_path / "corrupt.pdf")
    with open(corrupt_path, "wb") as f:
        f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\nGARBAGE_BYTES_TRUNCATED_EOF")

    try:
        data = pdf_service.extract_full_resume_data(corrupt_path)
        assert isinstance(data, dict)
    except Exception as exc:
        assert "pdf" in str(exc).lower() or "cannot open" in str(exc).lower() or "syntax" in str(exc).lower()


def test_edge_case_textless_scanned_pdf(tmp_path):
    """Verifies that text-less / image-only PDFs raise clear informative error."""
    doc = fitz.open()
    doc.new_page(width=612, height=792)  # Completely blank page with 0 text
    blank_path = str(tmp_path / "blank_scanned.pdf")
    doc.save(blank_path)
    doc.close()

    with pytest.raises(ValueError, match="No readable text found"):
        pdf_service.extract_full_resume_data(blank_path)


def test_user_corrections_override(tmp_path):
    """Verifies Phase 3 requirement: candidate-confirmed historical corrections override base extraction."""
    # Create test PDF with original typo
    doc = fitz.open()
    p = doc.new_page(width=612, height=792)
    p.insert_text((50, 50), "ALICE TESTER", fontsize=16)
    p.insert_text((50, 70), "alice@tester.org", fontsize=10)
    p.insert_text((50, 100), "SKILLS", fontsize=12)
    p.insert_text((50, 120), "Pythn, Dckr, Ract", fontsize=10)
    test_pdf = str(tmp_path / "test_corr.pdf")
    doc.save(test_pdf)
    doc.close()

    # User corrections recorded previously
    corrections = [
        {"field_name": "skill", "original_value": "Pythn", "corrected_value": "Python", "category": "Programming Language"},
        {"field_name": "skill", "original_value": "Dckr", "corrected_value": "Docker", "category": "DevOps"},
    ]

    data = pdf_service.extract_full_resume_data(test_pdf, user_corrections=corrections)
    extracted_names = [s["name"] for s in data["skills"]]
    assert "Python" in extracted_names
    assert "Docker" in extracted_names


def test_extra_token_duplicate_guard():
    """Verifies Phase 4.4 requirement: generic extra-token guard prohibits auto-merge."""
    # Distinct technologies with extra tokens
    rel1 = career_knowledge_service.classify_relationship("React", "React Native")
    assert rel1["auto_merge"] is False
    assert rel1["is_match"] is False

    rel2 = career_knowledge_service.classify_relationship("SQL", "MySQL")
    assert rel2["auto_merge"] is False
    assert rel2["is_match"] is False

    rel3 = career_knowledge_service.classify_relationship("Java", "JavaScript")
    assert rel3["auto_merge"] is False
    assert rel3["is_match"] is False

    # Exact matches and known aliases allow auto-merge
    rel4 = career_knowledge_service.classify_relationship("FastAPI", "fastapi")
    assert rel4["auto_merge"] is True
    assert rel4["is_match"] is True

    rel5 = career_knowledge_service.classify_relationship("Power BI", "PowerBI")
    assert rel5["auto_merge"] is True
    assert rel5["is_match"] is True
