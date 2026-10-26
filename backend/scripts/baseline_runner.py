import asyncio
import time
import json
import tracemalloc
import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pdf_service import pdf_service
from app.services.ai.ollama_provider import ollama_provider

async def run_baseline():
    pdf_path = "tests/fixtures/master_resume_reference.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "backend/tests/fixtures/master_resume_reference.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return

    tracemalloc.start()
    t_start = time.perf_counter()

    # 1. Plain PDF extraction
    t_pdf_start = time.perf_counter()
    plain_text = pdf_service.extract_text_from_pdf_plain(pdf_path)
    raw_text = pdf_service.extract_text_from_pdf(pdf_path)
    t_pdf_end = time.perf_counter()
    pdf_time = t_pdf_end - t_pdf_start

    # Reset ollama provider call metrics if tracked
    initial_stats = dict(getattr(ollama_provider, "_last_inference_stats", {}))

    # 2. Hybrid extraction
    t_hybrid_start = time.perf_counter()
    extracted_data = await pdf_service.extract_full_resume_data_hybrid(
        pdf_path, raw_text, plain_text=plain_text
    )
    t_hybrid_end = time.perf_counter()
    hybrid_time = t_hybrid_end - t_hybrid_start

    t_end = time.perf_counter()
    total_time = t_end - t_start
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Check ollama stats
    latest_stats = dict(getattr(ollama_provider, "_last_inference_stats", {}))

    # Load expected
    expected_path = "tests/fixtures/master_resume_reference.expected.json"
    if not os.path.exists(expected_path):
        expected_path = "backend/tests/fixtures/master_resume_reference.expected.json"
    
    with open(expected_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    # Evaluate extraction results
    skills_extracted = [
        s.get("name") if isinstance(s, dict) else str(s)
        for s in extracted_data.get("skills", [])
    ]
    skills_extracted_lower = {s.lower() for s in skills_extracted}

    expected_skills = expected.get("expected_skills", [])
    found_expected_skills = [s for s in expected_skills if s.lower() in skills_extracted_lower]
    missing_expected_skills = [s for s in expected_skills if s.lower() not in skills_extracted_lower]

    pi = extracted_data.get("personal_info", {})
    exp = extracted_data.get("experience", [])
    proj = extracted_data.get("projects", [])
    edu = extracted_data.get("education", [])
    certs = extracted_data.get("certifications", [])
    custom = extracted_data.get("custom_sections", [])

    results = {
        "metrics": {
            "total_time_seconds": round(total_time, 2),
            "pdf_extraction_seconds": round(pdf_time, 4),
            "hybrid_processing_seconds": round(hybrid_time, 2),
            "peak_memory_mb": round(peak_mem / (1024 * 1024), 2),
            "ollama_inference_stats": latest_stats
        },
        "counts": {
            "skills_count": len(skills_extracted),
            "projects_count": len(proj),
            "experience_count": len(exp),
            "education_count": len(edu),
            "certifications_count": len(certs),
            "custom_sections_count": len(custom)
        },
        "skills_evaluation": {
            "total_extracted": len(skills_extracted),
            "expected_count": len(expected_skills),
            "found_count": len(found_expected_skills),
            "missing_expected_skills": missing_expected_skills,
            "sample_extracted_skills": skills_extracted[:15]
        },
        "personal_info_accuracy": {
            "name": pi.get("name"),
            "email": pi.get("email"),
            "phone": pi.get("phone"),
            "location": pi.get("location"),
            "github_url": pi.get("github_url"),
            "linkedin_url": pi.get("linkedin_url"),
            "portfolio_url": pi.get("portfolio_url")
        },
        "structure_summary": {
            "has_experience": len(exp) > 0,
            "has_projects": len(proj) > 0,
            "has_education": len(edu) > 0,
            "has_certifications": len(certs) > 0,
            "project_titles": [p.get("title") for p in proj],
            "experience_companies": [e.get("company") for e in exp]
        }
    }

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(run_baseline())
