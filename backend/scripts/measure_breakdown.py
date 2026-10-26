import time
import os
import sys
import json
import psutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pdf_service import pdf_service
from app.services.career_knowledge_service import career_knowledge_service
from app.core.database import SessionLocal
from app.models.resume import MasterResume

def measure():
    pdf_path = "tests/fixtures/master_resume_reference.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "backend/tests/fixtures/master_resume_reference.pdf"

    proc = psutil.Process()
    rss_start = proc.memory_info().rss / 1024 / 1024

    # 1. PDF layout and links
    t0 = time.perf_counter()
    plain_text = pdf_service.extract_text_from_pdf_plain(pdf_path)
    raw_text = pdf_service.extract_text_from_pdf(pdf_path)
    layout = pdf_service.extract_layout_lines(pdf_path)
    links = pdf_service.extract_links_from_pdf(pdf_path)
    t1 = time.perf_counter()
    pdf_layout_time = t1 - t0

    # 2. Section segmentation
    t2 = time.perf_counter()
    sections = pdf_service.segment_sections(raw_text, layout)
    t3 = time.perf_counter()
    segmentation_time = t3 - t2

    # 3. Model load time (if not loaded)
    t4 = time.perf_counter()
    model = career_knowledge_service._get_sentence_transformer()
    t5 = time.perf_counter()
    model_load_time = t5 - t4

    # 4. Entity extraction
    t6 = time.perf_counter()
    extracted_data = pdf_service.extract_full_resume_data(pdf_path, raw_text=raw_text)
    t7 = time.perf_counter()
    entity_extraction_time = t7 - t6

    # 5. Embedding inference for extracted skills
    skills = extracted_data.get("skills", [])
    t8 = time.perf_counter()
    for s in skills:
        s_name = s.get("name", "") if isinstance(s, dict) else str(s)
        career_knowledge_service.generate_embedding(s_name)
    t9 = time.perf_counter()
    embedding_inference_time = t9 - t8

    rss_peak = proc.memory_info().rss / 1024 / 1024

    # 6. DB write simulation
    db = SessionLocal()
    t10 = time.perf_counter()
    # Read/write test record
    res = db.query(MasterResume).first()
    db.commit()
    t11 = time.perf_counter()
    db_write_time = t11 - t10
    db.close()

    result = {
        "pdf_layout_links_seconds": round(pdf_layout_time, 4),
        "section_segmentation_seconds": round(segmentation_time, 4),
        "embedding_model_load_seconds": round(model_load_time, 4),
        "entity_extraction_seconds": round(entity_extraction_time, 4),
        "embedding_inference_seconds": round(embedding_inference_time, 4),
        "db_write_seconds": round(db_write_time, 4),
        "total_component_time_seconds": round(pdf_layout_time + segmentation_time + entity_extraction_time + embedding_inference_time + db_write_time, 4),
        "skills_count": len(skills),
        "rss_start_mb": round(rss_start, 2),
        "rss_peak_mb": round(rss_peak, 2)
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    measure()
