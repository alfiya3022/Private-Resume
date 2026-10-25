import os
import sys
import json
import glob
from difflib import SequenceMatcher

# Ensure app is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.services.pdf_service import pdf_service

def sim(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, str(a).lower().strip(), str(b).lower().strip()).ratio()

def match_items(expected_list, extracted_list, key_fn=None, threshold=0.60):
    if not expected_list and not extracted_list:
        return 1.0, 1.0, 1.0
    if not expected_list:
        return 0.0, 1.0, 0.0
    if not extracted_list:
        return 1.0, 0.0, 0.0

    matched_ext = set()
    tp = 0
    for exp in expected_list:
        exp_val = key_fn(exp) if key_fn else exp
        best_idx = None
        best_s = 0.0
        for idx, ext in enumerate(extracted_list):
            if idx in matched_ext:
                continue
            ext_val = key_fn(ext) if key_fn else ext
            s = sim(exp_val, ext_val)
            if s > best_s:
                best_s = s
                best_idx = idx
        if best_s >= threshold and best_idx is not None:
            tp += 1
            matched_ext.add(best_idx)

    precision = tp / len(extracted_list) if extracted_list else 0.0
    recall = tp / len(expected_list) if expected_list else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1

def score_document(pdf_path, expected_path):
    with open(expected_path, "r", encoding="utf-8") as f:
        exp = json.load(f)

    ext = pdf_service.extract_full_resume_data(pdf_path)

    # 1. Personal Info
    exp_pi = exp.get("personal_info", {})
    ext_pi = ext.get("personal_info", {})
    pi_fields = ["name", "email", "phone", "location"]
    pi_matches = 0
    pi_total = 0
    for f in pi_fields:
        if f in exp_pi and exp_pi[f]:
            pi_total += 1
            if sim(exp_pi[f], ext_pi.get(f, "")) >= 0.70:
                pi_matches += 1
    pi_acc = (pi_matches / pi_total) if pi_total > 0 else 1.0

    # 2. Skills
    exp_skills = [s["name"] if isinstance(s, dict) else s for s in exp.get("skills", [])]
    ext_skills = [s["name"] if isinstance(s, dict) else s for s in ext.get("skills", [])]
    sk_p, sk_r, sk_f1 = match_items(exp_skills, ext_skills, threshold=0.75)

    # 3. Projects
    exp_projs = exp.get("projects", [])
    ext_projs = ext.get("projects", [])
    pr_p, pr_r, pr_f1 = match_items(exp_projs, ext_projs, key_fn=lambda x: x.get("title", ""), threshold=0.55)

    # 4. Experience
    exp_exps = exp.get("experience", [])
    ext_exps = ext.get("experience", [])
    ex_p, ex_r, ex_f1 = match_items(exp_exps, ext_exps, key_fn=lambda x: f"{x.get('title','')} {x.get('company','')}", threshold=0.50)

    # 5. Education
    exp_edus = exp.get("education", [])
    ext_edus = ext.get("education", [])
    ed_p, ed_r, ed_f1 = match_items(exp_edus, ext_edus, key_fn=lambda x: f"{x.get('degree','')} {x.get('institution','')}", threshold=0.45)

    # 6. Certifications
    exp_certs = exp.get("certifications", [])
    ext_certs = ext.get("certifications", [])
    ce_p, ce_r, ce_f1 = match_items(exp_certs, ext_certs, key_fn=lambda x: x.get("name", ""), threshold=0.50)

    # Preserved sections & Needs review
    custom_secs = ext.get("custom_sections", {})
    n_preserved = len(custom_secs)
    n_review = ext.get("needs_review_count", 0)

    return {
        "doc": os.path.basename(pdf_path),
        "contact_acc": pi_acc,
        "skills_p": sk_p, "skills_r": sk_r, "skills_f1": sk_f1,
        "proj_f1": pr_f1,
        "exp_f1": ex_f1,
        "edu_f1": ed_f1,
        "cert_f1": ce_f1,
        "preserved": n_preserved,
        "needs_review": n_review,
    }

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "heldout", "real"))
    expected_dir = os.path.join(base_dir, "expected")

    pairs = [
        ("Alfiya_resume_DA.pdf", "Alfiya_resume_DA.expected.json"),
        ("Alfiya_Nvidia.pdf", "Alfiya_Nvidia.expected.json"),
        ("DATA_Resume_temp1.pdf", "DATA_Resume_temp1.expected.json"),
        ("DATA_Resume_temp4.pdf", "DATA_Resume_temp4.expected.json"),
        ("resume_DA.pdf", "resume_DA.expected.json"),
        ("resume template_2.pdf", "resume template_2.expected.json"),
    ]

    results = []
    for pdf_name, exp_name in pairs:
        pdf_path = os.path.join(base_dir, pdf_name)
        exp_path = os.path.join(expected_dir, exp_name)
        if not os.path.exists(pdf_path) or not os.path.exists(exp_path):
            print(f"Skipping {pdf_name}: missing file")
            continue
        res = score_document(pdf_path, exp_path)
        results.append(res)

    print("\n" + "=" * 115)
    print(f"{'Document':<24} | {'Contact':<7} | {'Skills (P/R/F1)':<15} | {'Proj F1':<7} | {'Exp F1':<7} | {'Edu F1':<7} | {'Cert F1':<7} | {'Pres':<4} | {'Rev':<4}")
    print("=" * 115)
    for r in results:
        sk_str = f"{r['skills_p']:.2f}/{r['skills_r']:.2f}/{r['skills_f1']:.2f}"
        print(f"{r['doc'][:24]:<24} | {r['contact_acc']*100:>6.1f}% | {sk_str:<15} | {r['proj_f1']:>7.2f} | {r['exp_f1']:>7.2f} | {r['edu_f1']:>7.2f} | {r['cert_f1']:>7.2f} | {r['preserved']:>4} | {r['needs_review']:>4}")
    print("=" * 115 + "\n")

if __name__ == "__main__":
    main()
