"""Layout-aware PDF parsing and Master Resume extraction service powered by LayoutLMv3."""

import logging
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import fitz  # PyMuPDF
import pymupdf4llm
from rapidfuzz import fuzz

from app.core.diagnostics import ProcessingDiagnostics
from app.services.ai.layoutlm_service import layoutlm_service
from app.services.ai.record_grouping import (
    record_grouping_service,
    SkillList,
    is_bullet_line as _is_bullet_line,
    strip_bullet_prefix as _strip_bullet_prefix,
    normalize_unicode_text as _normalize_unicode_text,
    DATE_RANGE_REGEX,
    SINGLE_DATE_REGEX,
    CANONICAL_SKILL_CASING,
    SKILL_TAXONOMY,
)

logger = logging.getLogger(__name__)


def normalize_unicode_text(text: str) -> str:
    """Normalizes Unicode text while preserving meaningful dashes and quotes."""
    return _normalize_unicode_text(text)


def clean_resume_markdown(text: str) -> str:
    """Converts Markdown text returned by PyMuPDF4LLM into clean plain resume text."""
    if not text:
        return ""
    # Convert html line breaks to newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    # Remove html tags
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    # Remove markdown table separator rows like |---|---|
    text = re.sub(r"^\s*\|[-:\s|]+\|\s*$", "", text, flags=re.MULTILINE)
    # Strip table pipes at line boundaries while preserving interior pipes
    text = re.sub(r"^\s*\|\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*\|\s*$", "", text, flags=re.MULTILINE)
    # Remove image tags
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    # [GitHub](url) -> GitHub
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # '## SKILLS' -> 'SKILLS'
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    # Page-break lines '-----'
    text = re.sub(r"^\s*-{3,}\s*$", "", text, flags=re.MULTILINE)
    # Bold and strikethrough markers
    text = text.replace("**", "").replace("__", "").replace("~~", "")
    # Italic markers
    text = re.sub(r"(?<![\w*])\*(?!\s)([^*\n]+?)\*(?![\w*])", r"\1", text)
    text = re.sub(r"(?<![\w_])_(?!\s)([^_\n]+?)_(?![\w_])", r"\1", text)
    # Bullet symbols -> '- '
    text = re.sub(r"^\s*[•●▪◦*\ufffd]\s+", "- ", text, flags=re.MULTILINE)
    # Join hyphenated line breaks
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _appears_in_source(needle: str, haystack: str, threshold: float = 0.6) -> bool:
    """Helper to check if needle or substantial words of needle appear in source text."""
    if not needle or not haystack:
        return False
    needle_low = needle.lower().strip()
    haystack_low = haystack.lower()
    if needle_low in haystack_low:
        return True
    words = [w for w in needle_low.split() if len(w) > 3]
    if not words:
        return False
    matches = sum(1 for w in words if w in haystack_low)
    return (matches / len(words)) >= threshold


class PdfService:
    """Master Resume Extraction service integrating PyMuPDF and LayoutLMv3."""

    SECTION_PATTERNS = {
        "summary": r"^(?:professional\s+|executive\s+)?(?:summary|profile|about\s+me|objective)",
        "skills": r"^(?:technical\s+|core\s+|key\s+)?(?:skills|competencies|technologies|tools|expertise|technical\s+exposure)",
        "experience": r"^(?:work\s+|professional\s+|relevant\s+|employment\s+)?(?:experience|employment|work\s+history|history)",
        "projects": r"^(?:key\s+|personal\s+|academic\s+|technical\s+|featured\s+)?(?:projects|portfolio)",
        "education": r"^(?:education|academic\s+background|academic\s+credentials|qualifications|academic\s+history)",
        "certifications": r"^(?:certifications?|certificates?|licenses?|courses?|awards?|achievements?|honors?)",
    }

    @classmethod
    def is_bullet_line(cls, text: str) -> bool:
        return _is_bullet_line(text)

    @classmethod
    def strip_bullet_prefix(cls, text: str) -> str:
        return _strip_bullet_prefix(text)

    def extract_text_from_pdf_plain(self, file_path: str) -> str:
        """Extracts plain raw text stream across all pages in PDF."""
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Could not open PDF file: {e}") from e

        try:
            if doc.is_encrypted:
                raise ValueError("Password-protected or encrypted PDFs are not supported.")
            return "\n".join(page.get_text() for page in doc).strip()
        finally:
            doc.close()

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extracts text using layout-aware PyMuPDF4LLM with fallback to plain extraction."""
        plain = self.extract_text_from_pdf_plain(file_path)
        try:
            md_raw = pymupdf4llm.to_markdown(file_path, write_images=False)
            cleaned = clean_resume_markdown(md_raw)
            if cleaned and len(cleaned.splitlines()) >= 0.8 * len(plain.splitlines()):
                return cleaned
        except Exception as e:
            logger.debug(f"pymupdf4llm extraction fallback: {e}")
        return plain

    def extract_links_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extracts clickable link annotations and their bounding boxes from PDF."""
        try:
            doc = fitz.open(file_path)
        except Exception:
            return []

        links: List[Dict[str, Any]] = []
        try:
            if doc.is_encrypted:
                return []
            for page_idx, page in enumerate(doc):
                for lk in page.get_links():
                    uri = lk.get("uri")
                    rect = lk.get("from")
                    if uri and rect:
                        links.append({
                            "uri": str(uri).strip(),
                            "rect": [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)],
                            "page": page_idx,
                        })
            return links
        finally:
            doc.close()

    def extract_layout_lines(self, file_path: str) -> List[Dict[str, Any]]:
        """Extracts lines from PDF with row reconstruction, typography, and geometrically matched links."""
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Could not open PDF file: {e}") from e

        all_lines: List[Dict[str, Any]] = []

        try:
            if doc.is_encrypted:
                raise ValueError("Password-protected or encrypted PDFs are not supported.")

            for page_idx, page in enumerate(doc):
                links = page.get_links()
                raw_blocks = [b for b in page.get_text("dict").get("blocks", []) if "lines" in b]

                for b in raw_blocks:
                    for l in b.get("lines", []):
                        spans = l.get("spans", [])
                        if not spans:
                            continue
                        line_text = " ".join(s.get("text", "").strip() for s in spans if s.get("text", "").strip())
                        if not line_text:
                            continue
                        line_bbox = [round(c, 1) for c in l.get("bbox", [0, 0, 0, 0])]
                        max_size = round(max((s.get("size", 10.0) for s in spans), default=10.0), 1)
                        has_bold = any(
                            (s.get("flags", 0) & 2 != 0)
                            or any(bld in (s.get("font") or "").lower() for bld in ["bold", "black", "heavy", "semibold", "medium"])
                            for s in spans
                        )
                        matched_links = []
                        for lk in links:
                            u = lk.get("uri")
                            rect = lk.get("from")
                            if u and rect:
                                if not (rect.x1 < line_bbox[0] - 2 or rect.x0 > line_bbox[2] + 2 or
                                        rect.y1 < line_bbox[1] - 2 or rect.y0 > line_bbox[3] + 2):
                                    matched_links.append(u)

                        all_lines.append({
                            "text": line_text,
                            "bbox": line_bbox,
                            "max_size": max_size,
                            "is_bold": has_bold,
                            "links": matched_links,
                            "page": page_idx,
                        })

            # Calculate baseline body size
            sizes = [l["max_size"] for l in all_lines]
            body_size = max(set(sizes), key=sizes.count) if sizes else 10.0
            for l in all_lines:
                l["body_size"] = body_size
                l["is_prominent"] = (l["max_size"] >= body_size * 1.15) or (l["is_bold"] and l["max_size"] >= body_size)

            return all_lines
        finally:
            doc.close()

    def segment_sections(
        self, raw_text: str, layout_lines: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, str]:
        """Segments resume lines into standard and custom sections."""
        if not layout_lines and raw_text:
            curr_sec = "header"
            res: Dict[str, str] = {}
            for raw_line in raw_text.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                clean = line.strip(":").strip()
                is_heading = (clean.isupper() and 1 <= len(clean.split()) <= 4)
                if is_heading:
                    for s in ["skills", "experience", "education", "projects", "summary", "certifications"]:
                        if s in clean.lower():
                            curr_sec = s
                            break
                    else:
                        curr_sec = clean
                    if curr_sec not in res:
                        res[curr_sec] = ""
                else:
                    res[curr_sec] = (res.get(curr_sec, "") + "\n" + line).strip()
            return {k: v for k, v in res.items() if v}

        lines = layout_lines if layout_lines else []
        standard_sec, custom_sec = record_grouping_service._segment_sections(lines)
        res: Dict[str, str] = {}
        for k, v in standard_sec.items():
            if v:
                res[k] = "\n".join(item["text"] for item in v if item.get("text")).strip()
        for k, v in custom_sec.items():
            if v:
                val = "\n".join(item["text"] for item in v if item.get("text")).strip()
                res[k] = val
                res[f"custom:{k}"] = val
        return res

    def _apply_user_corrections(self, result: Dict[str, Any], user_corrections: List[Any]) -> Dict[str, Any]:
        """Applies candidate-confirmed historical corrections to extraction result if similarity >= 0.85."""
        if not user_corrections:
            return result

        for corr in user_corrections:
            if hasattr(corr, "source_evidence") and getattr(corr, "source_type", None) == "user_correction":
                ev = corr.source_evidence or ""
                m = re.search(r"User corrected from '([^']+)' to '([^']+)'", ev)
                orig = m.group(1) if m else ""
                val = corr.original_text or (m.group(2) if m else "")
                field = corr.category or "skill"
            elif isinstance(corr, dict):
                orig = corr.get("original_value") or ""
                val = corr.get("corrected_value") or ""
                field = corr.get("field_name") or corr.get("category") or "skill"
            else:
                continue

            if not orig or not val:
                continue

            # Skill overrides
            for s in result.get("skills", []):
                s_name = s.get("name", "") if isinstance(s, dict) else str(s)
                if fuzz.ratio(s_name.lower(), orig.lower()) >= 85:
                    if isinstance(s, dict):
                        s["name"] = val
                        if field and field not in ("skill", "profile_field"):
                            s["category"] = field

            # Project overrides
            for p in result.get("projects", []):
                p_title = p.get("title", "")
                if fuzz.ratio(p_title.lower(), orig.lower()) >= 85:
                    p["title"] = val

            # Experience overrides
            for e in result.get("experience", []):
                e_comp = e.get("company", "")
                e_role = e.get("title", "")
                if fuzz.ratio(e_comp.lower(), orig.lower()) >= 85:
                    e["company"] = val
                elif fuzz.ratio(e_role.lower(), orig.lower()) >= 85:
                    e["title"] = val

            # Education overrides
            for ed in result.get("education", []):
                inst = ed.get("institution", "")
                deg = ed.get("degree", "")
                if fuzz.ratio(inst.lower(), orig.lower()) >= 85:
                    ed["institution"] = val
                elif fuzz.ratio(deg.lower(), orig.lower()) >= 85:
                    ed["degree"] = val

        return result

    def extract_full_resume_data(
        self,
        file_path: str,
        raw_text: Optional[str] = None,
        user_corrections: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Extracts complete candidate profile and career history using LayoutLMv3 and record grouping."""
        layout_lines = self.extract_layout_lines(file_path)
        if not layout_lines:
            raise ValueError("No readable text found in this PDF. Scanned or image-only PDFs are not supported.")

        # Check total characters across layout lines
        total_text_len = sum(len(l["text"].strip()) for l in layout_lines)
        if total_text_len == 0:
            raise ValueError("No readable text found in this PDF. Scanned or image-only PDFs are not supported.")

        links = self.extract_links_from_pdf(file_path)

        # Assemble layout tokens and structured records via record_grouping_service
        extracted_data = record_grouping_service.group_records(
            layout_lines=layout_lines,
            links=links,
            raw_text=raw_text,
        )

        # Wrap skills in SkillList to support both string containment and dict iteration
        raw_skills = extracted_data.get("skills", [])
        extracted_data["skills"] = SkillList(raw_skills)

        # Apply user corrections if available
        if user_corrections:
            extracted_data = self._apply_user_corrections(extracted_data, user_corrections)

        return extracted_data

    async def extract_full_resume_data_hybrid(
        self,
        file_path: str,
        raw_text: Optional[str] = None,
        plain_text: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extracts resume data with processing diagnostics."""
        diag = ProcessingDiagnostics(correlation_id=correlation_id)

        with diag.track_stage("pdf_layout_extraction", file_path=file_path):
            if not raw_text:
                raw_text = self.extract_text_from_pdf(file_path)

        with diag.track_stage("layoutlm_record_grouping"):
            result = self.extract_full_resume_data(file_path, raw_text=raw_text)

        result["diagnostics"] = diag.get_summary()
        return result

    def detect_skills_deterministically(self, text: str) -> List[str]:
        """Detects known technical skills in text without hallucinations."""
        found = []
        known_skills = [
            "Python", "Docker", "PostgreSQL", "React", "Tailwind", "Tailwind CSS",
            "FastAPI", "SQL", "JavaScript", "TypeScript", "Git", "Linux", "AWS", "Java", "C++", "C#"
        ]
        t_low = text.lower()
        for s in known_skills:
            pattern = r"(?<!\w)" + re.escape(s.lower()) + r"(?!\w)"
            if re.search(pattern, t_low):
                found.append(s)
        return found

    # Backward compatibility helper delegations
    def _extract_projects(self, proj_text: str, links: List[Dict[str, Any]], proj_layout: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        lines = proj_layout if proj_layout else [
            {"text": line.strip(), "bbox": [0, idx * 10, 100, idx * 10 + 10], "is_bold": False, "links": []}
            for idx, line in enumerate((proj_text or "").splitlines()) if line.strip()
        ]
        return record_grouping_service._extract_projects(lines, links)

    def _extract_experience(self, exp_text: str, exp_layout: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        lines = exp_layout if exp_layout else [
            {"text": line.strip(), "bbox": [0, idx * 10, 100, idx * 10 + 10], "is_bold": False, "links": []}
            for idx, line in enumerate((exp_text or "").splitlines()) if line.strip()
        ]
        return record_grouping_service._extract_experience(lines)

    def _extract_education(self, edu_text: str, edu_layout: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        lines = edu_layout if edu_layout else [
            {"text": line.strip(), "bbox": [0, idx * 10, 100, idx * 10 + 10], "is_bold": False, "links": []}
            for idx, line in enumerate((edu_text or "").splitlines()) if line.strip()
        ]
        return record_grouping_service._extract_education(lines)

    def _extract_certifications(self, cert_text: str, links: List[Dict[str, Any]], cert_layout: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        lines = cert_layout if cert_layout else [
            {"text": line.strip(), "bbox": [0, idx * 10, 100, idx * 10 + 10], "is_bold": False, "links": []}
            for idx, line in enumerate((cert_text or "").splitlines()) if line.strip()
        ]
        return record_grouping_service._extract_certifications(lines, [], links)

    def validate_and_ground_experience(self, items: List[Dict[str, Any]], source_text: str) -> List[Dict[str, Any]]:
        """Filters out fabricated companies or ungrounded bullet points."""
        grounded = []
        for it in items:
            comp = it.get("company", "")
            if comp and comp.lower() in source_text.lower():
                valid_bullets = [b for b in it.get("bullets", []) if any(w.lower() in source_text.lower() for w in b.split() if len(w) > 4)]
                new_it = dict(it)
                new_it["bullets"] = valid_bullets
                grounded.append(new_it)
        return grounded

    def validate_and_ground_projects(self, items: List[Dict[str, Any]], source_text: str, doc_links: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Verifies projects appear in source text and strips unverified links."""
        valid_links = set(doc_links or [])
        grounded = []
        for it in items:
            title = it.get("title", "")
            if title and any(w.lower() in source_text.lower() for w in title.split() if len(w) > 3):
                new_it = dict(it)
                if new_it.get("github_url") and new_it["github_url"] not in valid_links and new_it["github_url"] not in source_text:
                    new_it["github_url"] = ""
                if new_it.get("live_url") and new_it["live_url"] not in valid_links and new_it["live_url"] not in source_text:
                    new_it["live_url"] = ""
                grounded.append(new_it)
        return grounded

    def validate_and_ground_certifications(self, items: List[Dict[str, Any]], source_text: str, doc_links: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Verifies certifications appear in source text."""
        valid_links = set(doc_links or [])
        grounded = []
        for it in items:
            name = it.get("name", "")
            if name and any(w.lower() in source_text.lower() for w in name.split() if len(w) > 3):
                new_it = dict(it)
                if new_it.get("credential_url") and new_it["credential_url"] not in valid_links and new_it["credential_url"] not in source_text:
                    new_it["credential_url"] = ""
                grounded.append(new_it)
        return grounded


pdf_service = PdfService()
