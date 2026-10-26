import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pdf_service import pdf_service

HELDOUT_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "heldout")

def evaluate_doc(doc_name, expected_name):
    pdf_path = os.path.join(HELDOUT_DIR, doc_name)
    expected_path = os.path.join(HELDOUT_DIR, expected_name)
    
    with open(expected_path, "r", encoding="utf-8") as f:
        expected = json.load(f)
        
    if expected.get("is_scanned_image"):
        try:
            raw_text = pdf_service.extract_text_from_pdf(pdf_path)
            is_textless = not raw_text or len(raw_text.strip()) < 20
        except ValueError as e:
            is_textless = True
        return {
            "doc": doc_name,
            "status": "PASS" if is_textless else "FAIL",
            "is_textless": is_textless,
            "details": "Correctly detected 0 selectable text for scanned image: 'No readable text found in this PDF. Scanned or image-only PDFs are not supported.'"
        }
        
    raw_text = pdf_service.extract_text_from_pdf(pdf_path)
    extracted = pdf_service.extract_full_resume_data(pdf_path, raw_text=raw_text)
    
    # 1. Personal Info
    exp_pi = expected.get("personal_info", {})
    act_pi = extracted.get("personal_info", {})
    pi_correct = 0
    pi_missing = 0
    pi_wrong = 0
    for k, v in exp_pi.items():
        act_val = act_pi.get(k)
        if not act_val:
            pi_missing += 1
        elif v.lower() in act_val.lower() or act_val.lower() in v.lower():
            pi_correct += 1
        else:
            pi_wrong += 1
            
    # 2. Skills
    exp_skills = expected.get("expected_skills", [])
    act_skills = [
        s.get("name") if isinstance(s, dict) else str(s)
        for s in extracted.get("skills", [])
    ]
    act_skills_lower = {s.lower() for s in act_skills}
    
    skills_correct = sum(1 for s in exp_skills if s.lower() in act_skills_lower)
    skills_missing = sum(1 for s in exp_skills if s.lower() not in act_skills_lower)
    # Extra skills extracted that were not expected
    exp_skills_lower = {s.lower() for s in exp_skills}
    skills_hallucinated = sum(1 for s in act_skills if s.lower() not in exp_skills_lower)
    
    # 3. Sections presence
    has_exp = len(extracted.get("experience", [])) > 0
    has_proj = len(extracted.get("projects", [])) > 0
    has_edu = len(extracted.get("education", [])) > 0
    has_certs = len(extracted.get("certifications", [])) > 0
    has_custom = len(extracted.get("custom_sections", {})) > 0
    
    return {
        "doc": doc_name,
        "personal_info": {"correct": pi_correct, "missing": pi_missing, "wrong": pi_wrong},
        "skills": {"correct": skills_correct, "missing": skills_missing, "hallucinated": skills_hallucinated, "total_extracted": len(act_skills)},
        "counts": {
            "experience": len(extracted.get("experience", [])),
            "projects": len(extracted.get("projects", [])),
            "education": len(extracted.get("education", [])),
            "certifications": len(extracted.get("certifications", [])),
            "custom_sections": len(extracted.get("custom_sections", {}))
        },
        "extracted_data": {
            "name": act_pi.get("name"),
            "email": act_pi.get("email"),
            "phone": act_pi.get("phone"),
            "location": act_pi.get("location"),
            "sample_skills": act_skills[:10]
        }
    }

if __name__ == "__main__":
    report = {}
    docs = [
        ("doc1_two_column_sidebar.pdf", "doc1.expected.json"),
        ("doc2_title_case_headings.pdf", "doc2.expected.json"),
        ("doc3_unlinked_plain_urls.pdf", "doc3.expected.json"),
        ("doc4_fresher_achievements.pdf", "doc4.expected.json"),
        ("doc5_scanned_image_only.pdf", "doc5.expected.json")
    ]
    for doc_pdf, doc_json in docs:
        report[doc_pdf] = evaluate_doc(doc_pdf, doc_json)
        
    print(json.dumps(report, indent=2))
