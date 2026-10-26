import re
import math
import logging
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from rapidfuzz import fuzz, utils as fuzz_utils

from app.models.profile import CareerKnowledgeItem, CandidateSkill
from app.core.config import settings

logger = logging.getLogger(__name__)

# Canonical industry aliases and standard normalizations
KNOWN_TECH_ALIASES: Dict[str, Dict[str, Any]] = {
    "postgres": {"canonical": "PostgreSQL", "aliases": ["postgresql", "pgsql", "postgres db"]},
    "postgresql": {"canonical": "PostgreSQL", "aliases": ["postgres", "pgsql", "postgres db"]},
    "react": {"canonical": "React", "aliases": ["reactjs", "react.js"]},
    "react native": {"canonical": "React Native", "aliases": ["react-native"]},
    "react.js": {"canonical": "React", "aliases": ["react", "reactjs"]},
    "node": {"canonical": "Node.js", "aliases": ["nodejs", "node.js"]},
    "node.js": {"canonical": "Node.js", "aliases": ["node", "nodejs"]},
    "aws": {"canonical": "AWS", "aliases": ["amazon web services", "aws cloud"]},
    "amazon web services": {"canonical": "AWS", "aliases": ["aws"]},
    "gcp": {"canonical": "GCP", "aliases": ["google cloud platform", "google cloud"]},
    "k8s": {"canonical": "Kubernetes", "aliases": ["kubernetes"]},
    "kubernetes": {"canonical": "Kubernetes", "aliases": ["k8s"]},
    "mongo": {"canonical": "MongoDB", "aliases": ["mongodb"]},
    "mongodb": {"canonical": "MongoDB", "aliases": ["mongo"]},
    "golang": {"canonical": "Go", "aliases": ["go"]},
    "go": {"canonical": "Go", "aliases": ["golang", "go language"]},
    "ts": {"canonical": "TypeScript", "aliases": ["typescript"]},
    "js": {"canonical": "JavaScript", "aliases": ["javascript"]},
    "ms sql server": {"canonical": "MS SQL Server", "aliases": ["microsoft sql server", "mssql"]},
    "t-sql": {"canonical": "T-SQL", "aliases": ["tsql", "transact-sql"]},
    "rest": {"canonical": "REST APIs", "aliases": ["rest api", "restful", "restful api", "restful apis"]},
    "ci/cd": {"canonical": "CI/CD", "aliases": ["cicd", "continuous integration", "continuous deployment"]},
    "docker": {"canonical": "Docker", "aliases": ["containerization", "containers"]},
    "excel": {"canonical": "Microsoft Excel", "aliases": ["ms excel", "spreadsheets"]},
    "power bi": {"canonical": "Power BI", "aliases": ["powerbi", "ms power bi", "power-bi"]},
    "powerbi": {"canonical": "Power BI", "aliases": ["power bi", "ms power bi", "power-bi"]},
    "window functions": {"canonical": "Window Functions", "aliases": ["windowfunctions", "window function", "windowfunction"]},
    "windowfunctions": {"canonical": "Window Functions", "aliases": ["window functions", "window function", "windowfunction"]},
    "fastapi": {"canonical": "FastAPI", "aliases": ["fast api"]},
    "fast api": {"canonical": "FastAPI", "aliases": ["fastapi"]},
}

# Known distinct technology pairs that must never be conflated as duplicates or aliases
KNOWN_DISTINCT_PAIRS: set = {
    frozenset(["sql", "mysql"]),
    frozenset(["java", "javascript"]),
    frozenset(["react", "react native"]),
    frozenset(["c", "c++"]),
    frozenset(["c", "c#"]),
    frozenset(["c++", "c#"]),
}

# Generic token and character-level difference guard prevents conflating distinct or
# hierarchical technologies (e.g. 'React' vs 'React Native', 'SQL' vs 'MySQL', 'C' vs 'C++')
# without relying on brittle hardcoded pair lists.
def has_extra_tokens_or_subconcept(term_a: str, term_b: str) -> bool:
    """Detects if one term contains the other plus extra tokens or non-trivial prefixes/suffixes,
    meaning auto-merge must be prohibited and explicit user consent is required."""
    a = term_a.strip().lower()
    b = term_b.strip().lower()
    if a == b:
        return False
    tokens_a = set(re.findall(r"[a-z0-9]+", a))
    tokens_b = set(re.findall(r"[a-z0-9]+", b))
    if tokens_a != tokens_b:
        if tokens_a.issubset(tokens_b) or tokens_b.issubset(tokens_a):
            return True
    # Character-level substring check for compound terms like "mysql" vs "sql" or "c++" vs "c"
    alnum_a = re.sub(r"[^a-z0-9]", "", a)
    alnum_b = re.sub(r"[^a-z0-9]", "", b)
    if alnum_a != alnum_b:
        if (len(alnum_a) >= 2 and alnum_a in alnum_b) or (len(alnum_b) >= 2 and alnum_b in alnum_a):
            return True
        # Symbol-differentiated variants (e.g. 'c' vs 'c++', 'c#')
        if (a in b or b in a) and abs(len(a) - len(b)) <= 3:
            return True
    return False



def normalize_term(term: Optional[str]) -> str:
    """Normalizes term for comparison: trims whitespace and canonicalizes casing."""
    if not term:
        return ""
    clean = re.sub(r"\s+", " ", str(term).strip())
    lower = clean.lower()
    if lower in KNOWN_TECH_ALIASES:
        return KNOWN_TECH_ALIASES[lower]["canonical"]
    return clean


def compute_deterministic_vector(text: str, dim: int = 384) -> List[float]:
    """Generates a normalized deterministic n-gram float vector (dimension 384)

    used as a reliable semantic fallback when external models are not available.
    """
    clean = text.lower().strip()
    vector = [0.0] * dim
    if not clean:
        return vector

    # Character trigrams hashing
    for i in range(len(clean) - 2):
        trigram = clean[i:i + 3]
        idx = abs(hash(trigram)) % dim
        vector[idx] += 1.0

    # Word tokens hashing
    words = re.findall(r"\w+", clean)
    for w in words:
        idx = abs(hash(w)) % dim
        vector[idx] += 2.0

    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 0:
        vector = [round(x / norm, 5) for x in vector]
    return vector


def cosine_similarity(vec_a: Optional[List[float]], vec_b: Optional[List[float]]) -> float:
    """Calculates cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


class CareerKnowledgeService:
    """Manages persistent career knowledge across master resumes, job descriptions,

    and user-confirmed corrections, supporting fuzzy matching, semantic retrieval,
    and clear provenance tracking.
    """

    def __init__(self):
        self._st_model = None
        self._st_checked = False

    def _get_sentence_transformer(self):
        """Lazy loader for SentenceTransformer ('BAAI/bge-small-en-v1.5')."""
        if not self._st_checked:
            self._st_checked = True
            model_name = getattr(settings, "EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer(model_name)
                logger.info("SentenceTransformer model loaded: %s", model_name)
            except Exception as e:
                logger.error(
                    "CRITICAL: Failed to load SentenceTransformer model '%s': %s. "
                    "Action required: verify container dependencies and HF cache.",
                    model_name,
                    e,
                    exc_info=True,
                )
                self._st_model = None
        return self._st_model

    @property
    def is_model_available(self) -> bool:
        """Indicates whether the real sentence-transformer model is loaded and ready."""
        return self._get_sentence_transformer() is not None

    def generate_embedding(self, text: str, allow_fallback: bool = False) -> List[float]:
        """Generates a 384-dimensional embedding for text using the real sentence-transformer model.

        Fails loudly with an actionable error rather than silently degrading to fallback vectors.
        Fallback is only permitted if allow_fallback=True (e.g. lightweight isolated unit tests).
        """
        model = self._get_sentence_transformer()
        if model is not None:
            try:
                vec = model.encode(text, normalize_embeddings=True)
                return [round(float(x), 5) for x in vec.tolist()]
            except Exception as e:
                logger.error(f"Inference error with sentence-transformer model: {e}", exc_info=True)
                if not allow_fallback:
                    raise RuntimeError(f"Embedding generation failed: {e}") from e

        if not allow_fallback:
            model_name = getattr(settings, "EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
            logger.error(
                f"Embedding model '{model_name}' is not loaded. Cannot generate semantic embedding. "
                "Failing loudly to prevent silent degradation to fallback vectors."
            )
            raise RuntimeError(
                f"Embedding model '{model_name}' is not available in the current environment. "
                "Ensure torch CPU and sentence-transformers are installed."
            )

        # Deterministic 384-dimensional fallback (only used when explicitly permitted)
        logger.warning("Using deterministic fallback embedding (allow_fallback=True)")
        return compute_deterministic_vector(text, dim=384)

    def generate_embeddings_batch(self, texts: List[str], allow_fallback: bool = False) -> List[List[float]]:
        """Generates 384-dimensional embeddings in a single batch forward pass for speed."""
        if not texts:
            return []
        model = self._get_sentence_transformer()
        if model is not None:
            try:
                vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                return [[round(float(x), 5) for x in vec.tolist()] for vec in vecs]
            except Exception as e:
                logger.error(f"Inference error with sentence-transformer batch model: {e}", exc_info=True)
                if not allow_fallback:
                    raise RuntimeError(f"Batch embedding generation failed: {e}") from e

        if not allow_fallback:
            model_name = getattr(settings, "EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
            raise RuntimeError(f"Embedding model '{model_name}' is not available in the current environment.")

        return [compute_deterministic_vector(t, dim=384) for t in texts]

    def reembed_all_knowledge_items(self, db: Session) -> int:
        """Regenerates embeddings for all active career knowledge items using the real model.

        Ensures that existing records match the BAAI/bge-small-en-v1.5 embedding space.
        Returns the number of updated records.
        """
        items = db.query(CareerKnowledgeItem).filter(CareerKnowledgeItem.review_status != "rejected").all()
        updated = 0
        for item in items:
            term = item.normalized_term or item.original_text
            if term:
                item.embedding = self.generate_embedding(term)
                updated += 1
        if updated > 0:
            db.commit()
            logger.info("Regenerated real embeddings for %d CareerKnowledgeItem records.", updated)
        return updated

    def classify_relationship(
        self, term_a: str, term_b: str, vec_a: Optional[List[float]] = None, vec_b: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Distinguishes between Exact match, Known alias, Semantically related concept,
        Broader/narrower concept, or Uncertain relationship. Auto-merge is only permitted
        for exact matches and explicit confirmed aliases.
        """
        a_clean = term_a.strip().lower()
        b_clean = term_b.strip().lower()

        # 0. Explicit distinct technologies guard (never conflated)
        if frozenset([a_clean, b_clean]) in KNOWN_DISTINCT_PAIRS:
            return {
                "relationship": "Distinct technologies",
                "score": 0.0,
                "confidence": 100,
                "is_match": False,
                "auto_merge": False,
            }

        # 1. Exact match (case/punctuation/spacing normalized identical)
        a_alnum = re.sub(r"[^a-z0-9]", "", a_clean)
        b_alnum = re.sub(r"[^a-z0-9]", "", b_clean)
        if a_clean == b_clean or normalize_term(a_clean).lower() == normalize_term(b_clean).lower() or (a_alnum and a_alnum == b_alnum):
            return {
                "relationship": "Exact match",
                "score": 1.0,
                "confidence": 100,
                "is_match": True,
                "auto_merge": True,
            }

        # 2. Known alias
        a_meta = KNOWN_TECH_ALIASES.get(a_clean)
        b_meta = KNOWN_TECH_ALIASES.get(b_clean)
        if (a_meta and b_clean in [a_meta["canonical"].lower()] + a_meta["aliases"]) or (
            b_meta and a_clean in [b_meta["canonical"].lower()] + b_meta["aliases"]
        ):
            return {
                "relationship": "Known alias",
                "score": 0.98,
                "confidence": 95,
                "is_match": True,
                "auto_merge": True,
            }

        # Extra tokens or substring guard: if one term contains the other plus extra tokens
        # (e.g. 'React' vs 'React Native', 'SQL' vs 'MySQL', 'Java' vs 'JavaScript', 'C' vs 'C++'),
        # auto-merge is strictly PROHIBITED; marked as broader/narrower concept requiring candidate consent.
        if has_extra_tokens_or_subconcept(term_a, term_b):
            return {
                "relationship": "Broader or narrower concept",
                "score": 0.75,
                "confidence": 85,
                "is_match": True,
                "auto_merge": False,
            }

        # Rapidfuzz string matching
        token_ratio = fuzz.token_sort_ratio(a_clean, b_clean) / 100.0
        partial_ratio = fuzz.partial_ratio(a_clean, b_clean) / 100.0

        if token_ratio >= 0.92:
            return {
                "relationship": "Exact match",
                "score": token_ratio,
                "confidence": 90,
                "is_match": True,
                "auto_merge": False,
            }

        # 3. Broader or narrower concept
        if (a_clean in b_clean or b_clean in a_clean) and (len(a_clean) >= 3 and len(b_clean) >= 3):
            return {
                "relationship": "Broader or narrower concept",
                "score": max(token_ratio, partial_ratio),
                "confidence": 80,
                "is_match": False,
                "auto_merge": False,
            }

        # 4. Semantic similarity
        v_a = vec_a or self.generate_embedding(term_a)
        v_b = vec_b or self.generate_embedding(term_b)
        sim = cosine_similarity(v_a, v_b)

        if sim >= 0.80:
            return {
                "relationship": "Semantically related concept",
                "score": round(sim, 3),
                "confidence": int(sim * 100),
                "is_match": False,
                "auto_merge": False,
            }

        # 5. Uncertain relationship
        sim_val = sim if 'sim' in locals() else (cosine_similarity(vec_a or self.generate_embedding(term_a), vec_b or self.generate_embedding(term_b)) or 0.0)
        return {
            "relationship": "Uncertain relationship",
            "score": round(sim_val, 3),
            "confidence": 30,
            "is_match": False,
            "auto_merge": False,
        }

    def record_knowledge_item(
        self,
        db: Session,
        user_id: int,
        knowledge_type: str,
        source_type: str,
        original_text: str,
        category: Optional[str] = None,
        source_id: Optional[str] = None,
        source_evidence: Optional[str] = None,
        source_page: Optional[int] = None,
        review_status: str = "extracted",
        confidence_score: int = 100,
        embedding: Optional[List[float]] = None,
    ) -> CareerKnowledgeItem:
        """Persists a career knowledge record, keeping candidate resume knowledge

        strictly isolated from job description knowledge.
        """
        normalized = normalize_term(original_text)
        aliases = []
        if original_text.lower() in KNOWN_TECH_ALIASES:
            aliases = KNOWN_TECH_ALIASES[original_text.lower()]["aliases"]

        # Check for existing record for this user, source, and normalized term
        existing = (
            db.query(CareerKnowledgeItem)
            .filter(
                CareerKnowledgeItem.user_id == user_id,
                CareerKnowledgeItem.source_type == source_type,
                CareerKnowledgeItem.normalized_term.ilike(normalized),
                CareerKnowledgeItem.knowledge_type == knowledge_type,
            )
            .first()
        )

        embedding_vector = embedding if embedding is not None else self.generate_embedding(normalized)

        if existing:
            existing.original_text = original_text
            existing.category = category or existing.category
            existing.source_evidence = source_evidence or existing.source_evidence
            existing.source_page = source_page or existing.source_page
            existing.review_status = review_status
            existing.confidence_score = confidence_score
            existing.embedding = embedding_vector
            db.commit()
            db.refresh(existing)
            return existing

        item = CareerKnowledgeItem(
            user_id=user_id,
            knowledge_type=knowledge_type[:50],
            source_type=source_type[:50],
            source_id=source_id[:100] if source_id else None,
            original_text=original_text[:255],
            normalized_term=normalized[:255],
            category=category[:100] if category else None,
            aliases=aliases,
            source_evidence=source_evidence,
            source_page=source_page,
            review_status=review_status[:50],
            confidence_score=confidence_score,
            embedding=embedding_vector,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def get_candidate_demonstrated_skills(
        self, db: Session, user_id: int
    ) -> List[CareerKnowledgeItem]:
        """Retrieves skills demonstrated by the candidate (from resume, profile, or user corrections).

        NEVER includes raw skills extracted from job descriptions.
        """
        return (
            db.query(CareerKnowledgeItem)
            .filter(
                CareerKnowledgeItem.user_id == user_id,
                CareerKnowledgeItem.knowledge_type == "skill",
                CareerKnowledgeItem.source_type.in_(["master_resume", "user_profile", "user_correction"]),
                CareerKnowledgeItem.review_status != "rejected",
            )
            .all()
        )

    def record_user_correction(
        self,
        db: Session,
        user_id: int,
        field_name: str,
        original_value: str,
        corrected_value: str,
        category: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> CareerKnowledgeItem:
        """Persists a candidate's correction during the extraction review process.

        Does not leak to or mutate other users' profiles.
        """
        return self.record_knowledge_item(
            db=db,
            user_id=user_id,
            knowledge_type="skill" if field_name == "skill" else "profile_field",
            source_type="user_correction",
            original_text=corrected_value,
            category=category,
            source_id=source_id,
            source_evidence=f"User corrected from '{original_value}' to '{corrected_value}'",
            review_status="confirmed",
            confidence_score=100,
        )

    def get_user_corrections(self, db: Session, user_id: int) -> List[CareerKnowledgeItem]:
        """Retrieves all confirmed user corrections previously recorded for this candidate."""
        return (
            db.query(CareerKnowledgeItem)
            .filter(
                CareerKnowledgeItem.user_id == user_id,
                CareerKnowledgeItem.source_type == "user_correction",
                CareerKnowledgeItem.review_status == "confirmed",
            )
            .all()
        )


career_knowledge_service = CareerKnowledgeService()
