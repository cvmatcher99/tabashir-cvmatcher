"""
Job-to-candidate matching with a weighted scoring model.
Optionally uses OpenAI embeddings for semantic skill similarity.
"""
from __future__ import annotations

import logging
import os
import re
from typing import List, Optional

from sqlalchemy.orm import Session

from database import Candidate, JobDescription, Skill
from schemas import MatchResult, CandidateOut, SkillOut

logger = logging.getLogger(__name__)

EDUCATION_RANK = {
    "high school": 0,
    "associate": 1, "diploma": 1, "certificate": 1,
    "bachelor": 2,
    "master": 3, "mba": 3, "msc": 3,
    "phd": 4, "doctorate": 4,
}

WEIGHTS = {"skill": 0.55, "experience": 0.30, "education": 0.15}


def _edu_rank(level: Optional[str]) -> int:
    if not level:
        return 0
    lvl = level.lower().strip()
    for key, rank in EDUCATION_RANK.items():
        if key in lvl:
            return rank
    return 0


def _skill_score(candidate_skills: List[str], required_skills: List[str]) -> tuple[float, List[str], List[str]]:
    if not required_skills:
        return 100.0, [], []
    c_set = {s.lower().strip() for s in candidate_skills}
    r_set = {s.lower().strip() for s in required_skills}
    matched = sorted(c_set & r_set)
    missing = sorted(r_set - c_set)
    score = len(matched) / len(r_set) * 100
    return round(score, 2), matched, missing


def _exp_score(candidate_exp: float, required_exp: float) -> float:
    if required_exp <= 0:
        return 100.0
    ratio = candidate_exp / required_exp
    if ratio >= 1.5:
        return 100.0
    if ratio >= 1.0:
        return 90.0 + (ratio - 1.0) * 20.0   # 90–100
    return min(ratio * 90.0, 90.0)


def _edu_score(candidate_level: Optional[str], required_level: Optional[str]) -> float:
    if not required_level:
        return 100.0
    c_rank = _edu_rank(candidate_level)
    r_rank = _edu_rank(required_level)
    if c_rank >= r_rank:
        return 100.0
    diff = r_rank - c_rank
    return max(0.0, 100.0 - diff * 25.0)


# ── OpenAI semantic boost ─────────────────────────────────────────────────────

def _semantic_skill_boost(candidate_skills: List[str], required_skills: List[str]) -> float:
    """Return 0–20 bonus points using embedding cosine similarity."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not required_skills or not candidate_skills:
        return 0.0
    try:
        from openai import OpenAI
        import numpy as np

        client = OpenAI(api_key=api_key)

        def embed(texts):
            resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
            return [d.embedding for d in resp.data]

        c_text = ", ".join(candidate_skills)
        r_text = ", ".join(required_skills)
        vecs = embed([c_text, r_text])
        a, b = vecs[0], vecs[1]
        cos = sum(x * y for x, y in zip(a, b)) / (
            (sum(x**2 for x in a) ** 0.5) * (sum(x**2 for x in b) ** 0.5) + 1e-9
        )
        return round(max(0.0, cos) * 20.0, 2)
    except Exception as exc:
        logger.debug("Semantic boost failed: %s", exc)
        return 0.0


# ── Extract skills from free-form job description text ───────────────────────

from cv_parser import KNOWN_SKILLS as _VOCAB

def extract_skills_from_text(text: str) -> List[str]:
    text_lower = text.lower()
    found = []
    for skill in _VOCAB:
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            found.append(skill)
    return found


def extract_experience_from_text(text: str) -> float:
    m = re.search(r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", text, re.I)
    return float(m.group(1)) if m else 0.0


# ── Main match function ───────────────────────────────────────────────────────

def match_candidates(job: JobDescription, db: Session) -> List[MatchResult]:
    candidates: List[Candidate] = db.query(Candidate).all()
    required_skill_names = [s.name for s in job.required_skills]
    results = []

    for cand in candidates:
        cand_skill_names = [s.name for s in cand.skills]

        raw_skill, matched, missing = _skill_score(cand_skill_names, required_skill_names)
        raw_exp = _exp_score(cand.years_experience, job.min_experience)
        raw_edu = _edu_score(cand.education_level, job.education_required)

        semantic = _semantic_skill_boost(cand_skill_names, required_skill_names)

        total = (
            raw_skill  * WEIGHTS["skill"]
            + raw_exp  * WEIGHTS["experience"]
            + raw_edu  * WEIGHTS["education"]
        ) + semantic

        total = round(min(total, 100.0), 2)

        results.append(
            MatchResult(
                candidate=CandidateOut(
                    id=cand.id,
                    full_name=cand.full_name,
                    email=cand.email,
                    phone=cand.phone,
                    years_experience=cand.years_experience,
                    education_level=cand.education_level,
                    education_field=cand.education_field,
                    file_name=cand.file_name,
                    created_at=cand.created_at,
                    skills=[SkillOut(id=s.id, name=s.name) for s in cand.skills],
                ),
                score=total,
                skill_score=round(raw_skill, 2),
                experience_score=round(raw_exp, 2),
                education_score=round(raw_edu, 2),
                matched_skills=matched,
                missing_skills=missing,
            )
        )

    results.sort(key=lambda r: r.score, reverse=True)
    return results
