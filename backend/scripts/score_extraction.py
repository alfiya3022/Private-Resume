import os
import sys
import json
from difflib import SequenceMatcher

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.services.pdf_service import pdf_service
from app.services.profile_service import profile_service

def sim(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, str(a).lower().strip(), str(b).lower().strip()).ratio()

def match_items(expected_list, extracted_list, key_fn=None, strict_fn=None, threshold=0.55):
    if not expected_list and not extracted_list:
        return (1.0, 1.0, 1.0), (1.0, 1.0, 1.0)
    if not expected_list:
        return (0.0, 1.0, 0.0), (0.0, 1.0, 0.0)
    if not extracted_list:
        return (1.0, 0.0, 0.0), (1.0, 0.0, 0.0)

    matched_ext_relaxed = set()
    matched_ext_strict = set()
    tp_relaxed = 0
    tp_strict = 0

    for exp in expected_list:
        exp_val = key_fn(exp) if key_fn else exp
        best_idx = None
        best_s = 0.0
        for idx, ext in enumerate(extracted_list):
            if idx in matched_ext_relaxed:
                continue
            ext_val = key_fn(ext) if key_fn else ext
            s = sim(exp_val, ext_val)
            if s > best_s:
                best_s = s
                best_idx = idx

        if best_s >= threshold and best_idx is not None:
            tp_relaxed += 1
            matched_ext_relaxed.add(best_idx)
            # Check strict matching (all required fields: dates, tech, bullet count, role/company)
            if strict_fn:
                if strict_fn(exp, extracted_list[best_idx]):
                    tp_strict += 1
                    matched_ext_strict.add(best_idx)
            else:
                tp_strict += 1

    p_rel = tp_relaxed / len(extracted_list) if extracted_list else 0.0
    r_rel = tp_relaxed / len(expected_list) if expected_list else 0.0
    f1_rel = (2 * p_rel * r_rel / (p_rel + r_rel)) if (p_rel + r_rel) > 0 else 0.0

    p_str = tp_strict / len(extracted_list) if extracted_list else 0.0
    r_str = tp_strict / len(expected_list) if expected_list else 0.0
    f1_str = (2 * p_str * r_str / (p_str + r_str)) if (p_str + r_str) > 0 else 0.0

    return (p_rel, r_rel, f1_rel), (p_str, r_str, f1_str)

def strict_proj(exp, ext):
    # Required: Title matched (by caller), Technologies overlap, bullet count within ±1, dates
    exp_tech = set(t.lower().strip() for t in exp.get("technologies", []))
    ext_tech = set(t.lower().strip() for t in ext.get("technologies", []))
    tech_ok = (len(exp_tech & ext_tech) > 0) if exp_tech else True

    exp_b = exp.get("bullet_count", len(exp.get("bullets", [])))
    ext_b = len(ext.get("bullets", []))
    b_ok = abs(exp_b - ext_b) <= 1 if exp_b > 0 else True

    exp_d = (exp.get("start_date") or "") + (exp.get("end_date") or "")
    ext_d = (ext.get("start_date") or "") + (ext.get("end_date") or "")
    date_ok = (sim(exp_d, ext_d) >= 0.40) if exp_d else True

    return tech_ok and b_ok and date_ok

def strict_exp(exp, ext):
    # Required: Title/Role matched, Company matched, bullet count within ±1, dates
    role_ok = sim(exp.get("title", ""), ext.get("title", "")) >= 0.50
    co_ok = sim(exp.get("company", ""), ext.get("company", "")) >= 0.40

    exp_b = exp.get("bullet_count", len(exp.get("bullets", [])))
    ext_b = len(ext.get("bullets", []))
    b_ok = abs(exp_b - ext_b) <= 1 if exp_b > 0 else True

    exp_d = (exp.get("start_date") or "") + (exp.get("end_date") or "")
    ext_d = (ext.get("start_date") or "") + (ext.get("end_date") or "")
    date_ok = (sim(exp_d, ext_d) >= 0.40) if exp_d else True

    return role_ok and co_ok and b_ok and date_ok

def strict_edu(exp, ext):
    # Required: Degree matched, Institution matched, grade/gpa if present, date
    deg_ok = sim(exp.get("degree", ""), ext.get("degree", "")) >= 0.40
    inst_ok = sim(exp.get("institution", ""), ext.get("institution", "")) >= 0.40

    grade_exp = (exp.get("grade") or "").strip()
    grade_ext = (ext.get("grade") or "").strip()
    grade_ok = (sim(grade_exp, grade_ext) >= 0.50) if grade_exp else True

    exp_d = (exp.get("graduation_date") or exp.get("end_date") or "")
    ext_d = (ext.get("graduation_date") or ext.get("end_date") or "")
    date_ok = (sim(exp_d, ext_d) >= 0.40) if exp_d else True

    return deg_ok and inst_ok and grade_ok and date_ok

def strict_cert(exp, ext):
    # Required: Name matched, Issuer matched, date if present
    name_ok = sim(exp.get("name", ""), ext.get("name", "")) >= 0.50
    iss_exp = (exp.get("issuer") or "").strip()
    iss_ext = (ext.get("issuer") or "").strip()
    iss_ok = (sim(iss_exp, iss_ext) >= 0.40) if iss_exp else True

    exp_d = (exp.get("issue_date") or exp.get("date") or "")
    ext_d = (ext.get("issue_date") or ext.get("date") or "")
    date_ok = (sim(exp_d, ext_d) >= 0.40) if exp_d else True

    return name_ok and iss_ok and date_ok

def score_document(pdf_path, expected_path):
    with open(expected_path, "r", encoding="utf-8") as f:
        exp = json.load(f)

    # EXACT execution path that the background task runs and that get_resume_extracted_data returns:
    raw_text = pdf_service.extract_text_from_pdf(pdf_path)
    extracted_data = pdf_service.extract_full_resume_data(pdf_path, raw_text=raw_text)
    ext = extracted_data

    # Contact Info
    exp_pi = exp.get("personal_info", {})
    ext_pi = ext.get("personal_info", {})
    pi_fields = ["name", "email", "phone", "location"]
    pi_matches = sum(1 for f in pi_fields if f in exp_pi and exp_pi[f] and sim(exp_pi[f], ext_pi.get(f, "")) >= 0.70)
    pi_total = sum(1 for f in pi_fields if f in exp_pi and exp_pi[f])
    pi_acc = (pi_matches / pi_total) if pi_total > 0 else 1.0

    # Skills (Relaxed and Strict)
    exp_skills = [s["name"] if isinstance(s, dict) else s for s in exp.get("skills", [])]
    ext_skills = [s["name"] if isinstance(s, dict) else s for s in ext.get("skills", [])]
    sk_rel, _ = match_items(exp_skills, ext_skills, threshold=0.75)

    # Projects (Relaxed: title only; Strict: title + dates + tech + bullets)
    pr_rel, pr_str = match_items(exp.get("projects", []), ext.get("projects", []),
                                 key_fn=lambda x: x.get("title", ""), strict_fn=strict_proj, threshold=0.55)

    # Experience (Relaxed: title/company; Strict: role + company + dates + bullets)
    ex_rel, ex_str = match_items(exp.get("experience", []), ext.get("experience", []),
                                 key_fn=lambda x: f"{x.get('title','')} {x.get('company','')}", strict_fn=strict_exp, threshold=0.45)

    # Education (Relaxed: degree/institution; Strict: degree + institution + dates + grade)
    ed_rel, ed_str = match_items(exp.get("education", []), ext.get("education", []),
                                 key_fn=lambda x: f"{x.get('degree','')} {x.get('institution','')}", strict_fn=strict_edu, threshold=0.40)

    # Certifications (Relaxed: name; Strict: name + issuer + dates)
    ce_rel, ce_str = match_items(exp.get("certifications", []), ext.get("certifications", []),
                                 key_fn=lambda x: x.get("name", ""), strict_fn=strict_cert, threshold=0.45)

    custom_secs = ext.get("custom_sections", {})
    n_preserved = len(custom_secs)

    return {
        "doc": os.path.basename(pdf_path),
        "contact_acc": pi_acc,
        "skills_p": sk_rel[0], "skills_r": sk_rel[1], "skills_f1": sk_rel[2],
        "proj_rel_f1": pr_rel[2], "proj_str_f1": pr_str[2],
        "exp_rel_f1": ex_rel[2], "exp_str_f1": ex_str[2],
        "edu_rel_f1": ed_rel[2], "edu_str_f1": ed_str[2],
        "cert_rel_f1": ce_rel[2], "cert_str_f1": ce_str[2],
        "preserved": n_preserved,
    }

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "heldout", "real"))
    expected_dir = os.path.join(base_dir, "expected")

    pairs = [
        ("Alfiya_resume_DA.pdf", "Alfiya_resume_DA.expected.json", "Alfiya_resume_DA.pdf (Reference LaTeX)"),
        ("Alfiya_Nvidia.pdf", "Alfiya_Nvidia.expected.json", "Alfiya_Nvidia.pdf (Single-page LaTeX)"),
        ("DATA_Resume_temp1.pdf", "DATA_Resume_temp1.expected.json", "DATA_Resume_temp1.pdf (Sidebar/Multi-column)"),
        ("DATA_Resume_temp4.pdf", "DATA_Resume_temp4.expected.json", "DATA_Resume_temp4.pdf (Symbol-delimited)"),
        ("resume_DA.pdf", "resume_DA.expected.json", "resume_DA.pdf (Word Plain via Print-to-PDF)"),
        ("resume template_2.pdf", "resume template_2.expected.json", "resume template_2.pdf (Icon-bullet Template)"),
    ]

    results = []
    for pdf_name, exp_name, label in pairs:
        pdf_path = os.path.join(base_dir, pdf_name)
        exp_path = os.path.join(expected_dir, exp_name)
        res = score_document(pdf_path, exp_path)
        res["label"] = label
        results.append(res)

    print("\n" + "=" * 138)
    print(f"{'Document File & Description':<44} | {'Contact':<7} | {'Skills (P/R/F1)':<16} | {'Proj (Strict)':<13} | {'Exp (Strict)':<12} | {'Edu (Strict)':<12} | {'Cert (Strict)':<13} | {'Pres':<4}")
    print("=" * 138)
    for r in results:
        sk_str = f"{r['skills_p']:.2f}/{r['skills_r']:.2f}/{r['skills_f1']:.2f}"
        pr = f"{r['proj_str_f1']:.2f}"
        ex = f"{r['exp_str_f1']:.2f}"
        ed = f"{r['edu_str_f1']:.2f}"
        ce = f"{r['cert_str_f1']:.2f}"
        print(f"{r['label']:<44} | {r['contact_acc']*100:>6.1f}% | {sk_str:<16} | {pr:<13} | {ex:<12} | {ed:<12} | {ce:<13} | {r['preserved']:>4}")
    print("=" * 138 + "\n")

if __name__ == "__main__":
    main()
