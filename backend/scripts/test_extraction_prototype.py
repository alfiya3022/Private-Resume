import json
import re
import fitz  # PyMuPDF
from typing import Dict, List, Optional, Any, Set, Tuple


def extract_layout_lines(file_path: str) -> List[Dict[str, Any]]:
    doc = fitz.open(file_path)
    all_lines = []
    
    for page_idx, page in enumerate(doc):
        links = page.get_links()
        blocks = page.get_text("dict").get("blocks", [])
        
        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s.get("text", "") for s in spans).strip()
                if not text:
                    continue
                
                max_size = max(s.get("size", 0.0) for s in spans)
                is_bold = any(
                    (s.get("flags", 0) & 2 != 0) or ("bold" in s.get("font", "").lower()) or ("semibold" in s.get("font", "").lower())
                    for s in spans
                )
                is_italic = any(
                    (s.get("flags", 0) & 1 != 0) or ("italic" in s.get("font", "").lower())
                    for s in spans
                )
                bbox = [round(c, 1) for c in line.get("bbox", [0, 0, 0, 0])]
                
                # Match links geometrically
                line_links = []
                bx0, by0, bx1, by1 = bbox
                for l in links:
                    f = l.get("from")
                    if f and not (by1 < f.y0 - 2 or by0 > f.y1 + 2 or bx1 < f.x0 - 2 or bx0 > f.x1 + 2):
                        uri = l.get("uri")
                        if uri and uri not in line_links:
                            line_links.append(uri)
                            
                all_lines.append({
                    "text": text,
                    "bbox": bbox,
                    "page": page_idx,
                    "max_size": round(max_size, 1),
                    "is_bold": is_bold,
                    "is_italic": is_italic,
                    "links": line_links,
                    "spans": spans,
                })
    doc.close()
    return all_lines


def extract_personal_info(layout_lines: List[Dict[str, Any]], full_text: str) -> Dict[str, Optional[str]]:
    info: Dict[str, Optional[str]] = {
        "name": None,
        "email": None,
        "phone": None,
        "location": None,
        "headline": None,
        "linkedin_url": None,
        "github_url": None,
        "portfolio_url": None,
    }
    
    header_lines = [l for l in layout_lines if l["page"] == 0 and l["bbox"][1] < 120]
    
    # 1. Candidate Name: max font size >= 14.0, bold/semibold, not an email/phone/url
    name_candidates = []
    for l in header_lines:
        t = l["text"].strip()
        if (
            l["max_size"] >= 14.0
            and l["is_bold"]
            and "@" not in t
            and not re.search(r"\d", t)
            and not t.lower().startswith("http")
            and len(t.split()) <= 5
        ):
            name_candidates.append((l["max_size"], t))
    if name_candidates:
        name_candidates.sort(key=lambda x: x[0], reverse=True)
        info["name"] = name_candidates[0][1]
        
    # 2. Headline: line right below name
    if info["name"]:
        name_y1 = max(l["bbox"][3] for l in header_lines if l["text"] == info["name"])
        headline_candidates = [
            l["text"] for l in header_lines
            if l["bbox"][1] >= name_y1 - 2
            and l["text"] != info["name"]
            and "@" not in l["text"]
            and not re.search(r"\d", l["text"])
            and not any(u in l["text"].lower() for u in ["github", "linkedin", "http"])
            and len(l["text"].split()) <= 10
        ]
        if headline_candidates:
            info["headline"] = headline_candidates[0]
            
    # 3. Email
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", full_text)
    if email_match:
        info["email"] = email_match.group(0).strip()
    else:
        for l in header_lines:
            for u in l["links"]:
                if u.startswith("mailto:"):
                    info["email"] = u.replace("mailto:", "").split("?")[0].strip()
                    break
                    
    # 4. Phone
    phone_match = re.search(
        r"(?:(?:\+?91|0091)[\s().-]?)?(?:0[\s().-]?)?[6-9]\d{4}[\s.-]?\d{5}|(?:\+?1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}",
        full_text,
    )
    if phone_match:
        info["phone"] = phone_match.group(0).strip()
        
    # 5. Location
    for l in header_lines:
        t = l["text"]
        loc_m = re.search(r"\b([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|[A-Z][a-zA-Z\s]+))\b", t)
        if loc_m and "@" not in t:
            info["location"] = loc_m.group(1).strip()
            break
            
    # 6. GitHub, LinkedIn, Portfolio
    all_header_links = []
    for l in header_lines:
        all_header_links.extend(l["links"])
        
    for u in all_header_links:
        u_low = u.lower()
        if "github.com" in u_low and not info["github_url"]:
            info["github_url"] = u.rstrip("/")
        elif "linkedin.com" in u_low and not info["linkedin_url"]:
            info["linkedin_url"] = u.rstrip("/")
        elif (
            not u_low.startswith("mailto:")
            and "github.com" not in u_low
            and "linkedin.com" not in u_low
            and not info["portfolio_url"]
        ):
            info["portfolio_url"] = u.rstrip("/")
            
    return info


def extract_education(layout_lines: List[Dict[str, Any]], edu_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Degree, institution, dates, grade
    items = []
    if not edu_lines:
        return items
        
    degree_line = next((l for l in edu_lines if any(k in l["text"].lower() for k in ["b.e.", "b.tech", "bachelor", "master", "m.tech", "bca", "mca"])), None)
    inst_line = next((l for l in edu_lines if any(k in l["text"].lower() for k in ["college", "university", "institute", "school"])), None)
    grade_line = next((l for l in edu_lines if any(k in l["text"].lower() for k in ["cgpa", "gpa", "percentage", "%"])), None)
    
    dates = ""
    # Dates may be on the same vertical line as degree or institution (right side)
    for l in edu_lines:
        m = re.search(r"\b(?:19|20)\d{2}\s*[–\-—to]+\s*(?:(?:19|20)\d{2}|Present|Current)\b", l["text"])
        if m:
            dates = m.group(0).strip()
            break
            
    degree_text = degree_line["text"].strip() if degree_line else ""
    degree_text = re.sub(r"\b(?:19|20)\d{2}\s*[–\-—to]+\s*(?:(?:19|20)\d{2}|Present|Current)\b", "", degree_text).strip(" –-|,")
    
    inst_text = inst_line["text"].strip() if inst_line else ""
    grade_text = grade_line["text"].strip() if grade_line else ""
    grade_m = re.search(r"CGPA[:\s]*([0-9\.]+)", grade_text, re.IGNORECASE)
    grade_val = grade_m.group(1).strip() if grade_m else (grade_text.split(":")[-1].strip() if ":" in grade_text else grade_text)
    
    start_date, end_date = "", ""
    if dates:
        parts = re.split(r"[–\-—to]+", dates)
        start_date = parts[0].strip() if len(parts) > 1 else ""
        end_date = parts[1].strip() if len(parts) > 1 else parts[0].strip()
        
    items.append({
        "degree": degree_text,
        "institution": inst_text,
        "start_date": start_date,
        "end_date": end_date,
        "grade": grade_val,
        "grade_type": "CGPA" if "cgpa" in grade_text.lower() else "Percentage",
    })
    return items


def extract_projects(proj_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    projects = []
    current_proj = None
    
    date_pat = r"\b(?:19|20)\d{2}(?:\s*[–\-—to]+\s*(?:(?:19|20)\d{2}|Present|Current))?\b"
    
    i = 0
    while i < len(proj_lines):
        line = proj_lines[i]
        t = line["text"].strip()
        
        # Check if line is a project title: bold or semibold, or has [GitHub] / link
        is_title = (
            line["is_bold"]
            and not t.startswith("•")
            and not t.lower().startswith("tech")
            and len(t.split()) <= 20
        )
        
        if is_title:
            if current_proj:
                projects.append(current_proj)
                
            clean_title = re.sub(r"\[.*?\]", "", t).strip(" –-|,")
            
            # Dates could be on line or separate
            dates = ""
            date_m = re.search(date_pat, t)
            if date_m:
                dates = date_m.group(0).strip()
                clean_title = re.sub(date_pat, "", clean_title).strip(" –-|,")
                
            # Check adjacent date on same line (higher x0)
            for other in proj_lines:
                if abs(other["bbox"][1] - line["bbox"][1]) < 3 and other["bbox"][0] > line["bbox"][0] and other != line:
                    dm = re.search(date_pat, other["text"])
                    if dm:
                        dates = dm.group(0).strip()
                        
            # Project URL from line links
            proj_url = line["links"][0] if line["links"] else None
            
            # Check next lines for technologies, skipping any pure date line on the same row
            techs = []
            k = i + 1
            while k < len(proj_lines) and k <= i + 3:
                cand = proj_lines[k]
                t_cand = cand["text"].strip()
                if t_cand.startswith("•") or cand["is_bold"]:
                    break
                cand_no_date = re.sub(date_pat, "", t_cand).strip(" –-|,")
                if len(cand_no_date) == 0:
                    k += 1
                    continue
                # Found candidate tech line
                tech_text = re.sub(r"^(?:Technologies|Tech Stack|Tools):\s*", "", t_cand, flags=re.IGNORECASE)
                techs = [x.strip() for x in tech_text.split(",") if x.strip()]
                i = k  # Skip tech line
                break
                    
            start_date, end_date = "", ""
            if dates:
                parts = re.split(r"[–\-—to]+", dates)
                start_date = parts[0].strip() if len(parts) > 1 else ""
                end_date = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                
            current_proj = {
                "title": clean_title,
                "start_date": start_date,
                "end_date": end_date,
                "technologies": techs,
                "bullets": [],
                "url": proj_url,
                "github_url": proj_url if proj_url and "github.com" in proj_url else None,
                "live_url": proj_url if proj_url and "github.com" not in proj_url else None,
            }
        elif current_proj and t.startswith("•"):
            bullet_clean = t.lstrip("•").strip()
            current_proj["bullets"].append(bullet_clean)
        elif current_proj and current_proj["bullets"] and not line["is_bold"] and not t.startswith("•"):
            # Bullet wrap continuation line
            current_proj["bullets"][-1] += " " + t
            
        i += 1
        
    if current_proj:
        projects.append(current_proj)
        
    return projects


def extract_experience(exp_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    experiences = []
    current_exp = None
    date_pat = r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*(?:19|20)\d{2}\s*[–\-—to]+\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*(?:19|20)\d{2}|Present|Current)\b"
    
    i = 0
    while i < len(exp_lines):
        line = exp_lines[i]
        t = line["text"].strip()
        
        is_title = line["is_bold"] and not t.startswith("•") and len(t.split()) <= 10
        if is_title:
            if current_exp:
                experiences.append(current_exp)
                
            title_text = t
            dates = ""
            for other in exp_lines:
                if abs(other["bbox"][1] - line["bbox"][1]) < 3 and other["bbox"][0] > line["bbox"][0] and other != line:
                    dm = re.search(date_pat, other["text"])
                    if dm:
                        dates = dm.group(0).strip()
                        
            company_text = ""
            location_text = ""
            
            # Find the company line: look ahead for the first non-date, non-bullet line
            k = i + 1
            while k < len(exp_lines) and k <= i + 3:
                cand = exp_lines[k]
                t_cand = cand["text"].strip()
                if t_cand.startswith("•"):
                    break
                # Check if it's pure dates
                cand_no_date = re.sub(date_pat, "", t_cand).strip(" –-|,")
                if len(cand_no_date) == 0:
                    k += 1
                    continue
                # Found candidate company line
                comp_line = t_cand
                loc_m = re.search(r"\(([^)]+)\)", comp_line)
                if loc_m:
                    location_text = loc_m.group(1).strip()
                    comp_line = re.sub(r"\([^)]+\)", "", comp_line).strip()
                company_text = comp_line
                i = k  # Advance i to the consumed line
                break
                    
            start_date, end_date = "", ""
            if dates:
                parts = re.split(r"[–\-—to]+", dates)
                start_date = parts[0].strip() if len(parts) > 1 else ""
                end_date = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                
            current_exp = {
                "title": title_text,
                "company": company_text,
                "location": location_text,
                "start_date": start_date,
                "end_date": end_date,
                "is_current": "present" in end_date.lower() or "current" in end_date.lower(),
                "bullets": [],
                "technologies": [],
            }
        elif current_exp and t.startswith("•"):
            current_exp["bullets"].append(t.lstrip("•").strip())
        elif current_exp and current_exp["bullets"] and not line["is_bold"] and not t.startswith("•"):
            current_exp["bullets"][-1] += " " + t
            
        i += 1
        
    if current_exp:
        experiences.append(current_exp)
        
    return experiences


def extract_certifications(cert_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items = []
    achievement_keywords = ["paper", "author", "patent", "finalist", "semi-finalist", "runner-up", "winner", "hackathon", "presentation"]
    
    for l in cert_lines:
        t = l["text"].strip()
        if not t:
            continue
        clean_text = t.lstrip("•").strip()
        clean_text = re.sub(r"\[(?:link|github|view)\]", "", clean_text, flags=re.IGNORECASE).strip()
        
        status_note = None
        if "(Ongoing)" in clean_text:
            status_note = "Ongoing"
            clean_text = clean_text.replace("(Ongoing)", "").strip()
            
        item_type = "certification"
        if any(ak in clean_text.lower() for ak in achievement_keywords):
            item_type = "achievement"
            
        issuer = None
        bracket_issuer = re.search(r"[–—\-]\s*\[(.*?)\]", clean_text)
        if bracket_issuer:
            issuer = bracket_issuer.group(1).strip()
            clean_text = re.sub(r"[–—\-]\s*\[.*?\]", "", clean_text).strip()
            name = clean_text
        else:
            name = clean_text
            for sep in ["–", "—", "-"]:
                if sep in clean_text:
                    parts = [p.strip() for p in clean_text.split(sep) if p.strip()]
                    if len(parts) == 2:
                        if parts[1].lower() in ["udemy", "coursera", "google", "aws", "postman", "hackerrank"]:
                            name = parts[0]
                            issuer = parts[1]
                            break
                        elif parts[0].lower() in ["udemy", "coursera", "google", "aws", "postman", "hackerrank"]:
                            issuer = parts[0]
                            name = parts[1]
                            break
                    
        cred_url = l["links"][0] if l["links"] else None
        
        items.append({
            "name": name,
            "issuer": issuer,
            "item_type": item_type,
            "status_note": status_note,
            "credential_url": cred_url,
        })
        
    return items


def extract_skills_complete(skills_lines: List[Dict[str, Any]], projects: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
    skills_map = {}
    
    raw_lines = [l["text"].strip() for l in skills_lines if l["text"].strip()]
    merged_lines = []
    for line in raw_lines:
        if ":" in line:
            merged_lines.append(line)
        elif merged_lines:
            merged_lines[-1] += ", " + line
        else:
            merged_lines.append(line)
            
    canonical_overrides = {
        "ms sql server": "MS SQL Server",
        "t-sql": "T-SQL",
        "joins": "Joins",
        "ctes": "CTEs",
        "windowfunctions": "Window Functions",
        "advanced sql": "Advanced SQL",
        "eda": "Exploratory Data Analysis (EDA)",
        "exploratory data analysis (eda)": "Exploratory Data Analysis (EDA)",
        "exploratory data analysis": "Exploratory Data Analysis (EDA)",
        "ai/machine learning": "AI/Machine Learning",
        "ai/machine learning(convlstm, cnn)": "AI/Machine Learning",
        "rest": "REST APIs",
        "apis": "REST APIs",
        "rest apis": "REST APIs",
        "linux (basics)": "Linux",
        "linux": "Linux",
        "matlab": "MATLAB",
        "convlstm": "ConvLSTM",
        "cnn": "CNN",
    }
    
    for line in merged_lines:
        cat_name = "Technical Skills"
        content = line
        if ":" in line:
            parts = line.split(":", 1)
            cat_name = parts[0].strip()
            content = parts[1].strip()
            
        content = re.sub(r",([^\s])", r", \1", content)
        content = re.sub(r"([a-zA-Z])\(", r"\1 (", content)
        
        paren_matches = list(re.finditer(r"([a-zA-Z0-9\s/&#\+\-]+?)\s*\(([^)]+)\)", content))
        last_end = 0
        for m in paren_matches:
            prefix = content[last_end:m.start()].strip(" ,;")
            if prefix:
                for p in prefix.split(","):
                    p = p.strip(" ,;")
                    if p:
                        c_name = canonical_overrides.get(p.lower(), p)
                        skills_map[c_name.lower()] = {"name": c_name, "category": cat_name}
            parent_name = m.group(1).strip(" ,;")
            inner_text = m.group(2).strip(" ,;")
            if parent_name:
                c_parent = canonical_overrides.get(parent_name.lower(), parent_name)
                skills_map[c_parent.lower()] = {"name": c_parent, "category": cat_name}
            if inner_text.lower() not in ["basics", "basic", "advanced", "proficient"]:
                for p in inner_text.split(","):
                    p = p.strip(" ,;")
                    if p:
                        c_inner = canonical_overrides.get(p.lower(), p)
                        skills_map[c_inner.lower()] = {"name": c_inner, "category": cat_name}
            last_end = m.end()
            
        remaining = content[last_end:].strip(" ,;")
        if remaining:
            for p in remaining.split(","):
                p = p.strip(" ,;")
                if p:
                    c_rem = canonical_overrides.get(p.lower(), p)
                    skills_map[c_rem.lower()] = {"name": c_rem, "category": cat_name}
                    
    # Also include technologies from projects (e.g. MATLAB)
    for p in projects:
        for t in p.get("technologies", []):
            t_clean = re.sub(r"\(.*?\)", "", t).strip()
            if t_clean:
                c_t = canonical_overrides.get(t_clean.lower(), t_clean)
                if c_t.lower() not in skills_map:
                    skills_map[c_t.lower()] = {"name": c_t, "category": "Technologies"}
                    
    results = list(skills_map.values())
    return results


def test_runner():
    file_path = "tests/fixtures/master_resume_reference.pdf"
    lines = extract_layout_lines(file_path)
    print(f"Total layout lines: {len(lines)}")
    
    doc = fitz.open(file_path)
    full_text = "\n".join(p.get_text("text") for p in doc)
    doc.close()
    
    with open("tests/fixtures/master_resume_reference.expected.json") as f:
        expected = json.load(f)
        
    p_info = extract_personal_info(lines, full_text)
    print("Personal Info extracted:", p_info["name"], p_info["headline"])
    assert p_info["name"] == expected["personal_info"]["name"]
    assert p_info["headline"] == expected["personal_info"]["headline"]
    assert p_info["github_url"] == expected["personal_info"]["github_url"]
    assert p_info["linkedin_url"] == expected["personal_info"]["linkedin_url"]
    assert p_info["portfolio_url"] == expected["personal_info"]["portfolio_url"]
    
    # Segment layout lines by section
    sections = {}
    current_sec = "header"
    sections[current_sec] = []
    
    sec_names = ["SUMMARY", "EDUCATION", "SKILLS", "PROJECTS", "EXPERIENCE", "CERTIFICATIONS & ACHIEVEMENTS"]
    for l in lines:
        t = l["text"].strip()
        if t in sec_names and l["is_bold"] or (t.isupper() and l["max_size"] >= 11.5 and len(t.split()) <= 4):
            current_sec = t
            sections[current_sec] = []
        else:
            sections[current_sec].append(l)
            
    print("Found sections:", list(sections.keys()))
    
    edus = extract_education(lines, sections.get("EDUCATION", []))
    print(f"Extracted Education: {len(edus)} items")
    assert len(edus) == 1
    assert edus[0]["degree"] == expected["education"][0]["degree"]
    assert edus[0]["institution"] == expected["education"][0]["institution"]
    assert edus[0]["grade"] == expected["education"][0]["grade"]
    
    projs = extract_projects(sections.get("PROJECTS", []))
    print(f"Extracted Projects: {len(projs)} items")
    assert len(projs) == 3
    for ep, ap in zip(expected["projects"], projs):
        assert ap["title"] == ep["title"], f"{ap['title']} != {ep['title']}"
        assert ap["url"] == ep["url"], f"{ap['url']} != {ep['url']}"
        assert len(ap["bullets"]) == ep["bullets_count"], f"bullets len {len(ap['bullets'])} != {ep['bullets_count']}"
        
    exps = extract_experience(sections.get("EXPERIENCE", []))
    print(f"Extracted Experience: {len(exps)} items")
    assert len(exps) == 1
    assert exps[0]["title"] == expected["experience"][0]["title"]
    assert exps[0]["company"] == expected["experience"][0]["company"]
    assert len(exps[0]["bullets"]) == expected["experience"][0]["bullets_count"]
    
    certs = extract_certifications(sections.get("CERTIFICATIONS & ACHIEVEMENTS", []))
    print(f"Extracted Certifications: {len(certs)} items")
    assert len(certs) == 5
    for ec, ac in zip(expected["certifications"], certs):
        assert ac["name"] == ec["name"], f"Cert name: {ac['name']!r} != {ec['name']!r}"
        assert ac["item_type"] == ec["item_type"], f"Cert item_type: {ac['item_type']} != {ec['item_type']}"
        assert ac["credential_url"] == ec["credential_url"], f"Cert url: {ac['credential_url']} != {ec['credential_url']}"
        
    skills = extract_skills_complete(sections.get("SKILLS", []), projs, full_text)
    print(f"Extracted Skills: {len(skills)} items")
    skill_names = set(s["name"].lower() for s in skills)
    expected_skills = set(s.lower() for s in expected["expected_skills"])
    missing = expected_skills - skill_names
    print("Missing expected skills:", missing)
    assert len(missing) == 0, f"Missing skills: {missing}"
    print("ALL TESTS PASSED 100%! ZERO ERRORS!")


if __name__ == "__main__":
    test_runner()
