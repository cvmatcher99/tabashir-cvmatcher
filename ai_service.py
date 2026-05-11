"""
Claude AI integration — CV parsing + job match explanations.
Uses claude-haiku-4-5 for speed and cost efficiency.
Falls back gracefully when ANTHROPIC_API_KEY is not set.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _client():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=key)
    except ImportError:
        logger.warning("anthropic package not installed")
        return None


# ── CV Parsing ─────────────────────────────────────────────────────────────────

def parse_cv_claude(text: str) -> Optional[Dict[str, Any]]:
    """Extract structured candidate data from raw CV text using Claude."""
    client = _client()
    if not client:
        return None
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Extract structured information from this CV. Return ONLY valid JSON with these exact keys:
full_name, email, phone, linkedin (URL or null), github (URL or null),
location (city/country or null), years_experience (number),
education_level (one of: PhD, Master, Bachelor, Associate, High School, or null),
education_field (string or null), skills (array of lowercase tech/professional skill strings).

CV TEXT:
\"\"\"
{text[:5000]}
\"\"\"

JSON only, no explanation:""",
            }],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
        data["years_experience"] = float(data.get("years_experience") or 0)
        data["skills"] = [s.lower().strip() for s in (data.get("skills") or [])]
        logger.info("Claude parsed CV: %s, %d skills", data.get("full_name"), len(data["skills"]))
        return data
    except Exception as e:
        logger.warning("Claude CV parse failed: %s", e)
        return None


# ── Job Match Explanation ──────────────────────────────────────────────────────

def explain_match(
    candidate_name: str,
    candidate_skills: List[str],
    candidate_exp: float,
    candidate_edu: Optional[str],
    job_title: str,
    required_skills: List[str],
    min_exp: float,
    edu_required: Optional[str],
    matched: List[str],
    missing: List[str],
    score: float,
) -> str:
    """Generate a 1–2 sentence personalised explanation for the match."""
    client = _client()

    if not client:
        return _fallback_explanation(candidate_exp, min_exp, matched, missing, score)

    try:
        prompt = f"""Write exactly 2 short sentences (max 55 words total) explaining why this job is a {score:.0f}% match for this candidate.
Be specific, positive, and mention concrete skills or experience. No bullet points.

Candidate: {candidate_name} | {candidate_exp} yrs exp | {candidate_edu or 'unspecified education'}
Candidate skills: {', '.join(candidate_skills[:12])}
Job: {job_title} | requires {min_exp}+ yrs | {edu_required or 'any education'}
Matched skills: {', '.join(matched[:6]) or 'none'}
Missing skills: {', '.join(missing[:4]) or 'none'}

2-sentence explanation:"""

        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=120,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        logger.debug("Claude explain failed: %s", e)
        return _fallback_explanation(candidate_exp, min_exp, matched, missing, score)


def _fallback_explanation(
    candidate_exp: float, min_exp: float,
    matched: List[str], missing: List[str], score: float,
) -> str:
    parts = []
    if matched:
        top = ", ".join(matched[:3])
        parts.append(f"Your skills in {top} align well with this role")
    if candidate_exp >= (min_exp or 0):
        parts.append("your experience meets the requirement")
    elif min_exp > 0:
        parts.append(f"consider building more experience to meet the {min_exp}-year requirement")
    if missing:
        parts.append(f"adding {', '.join(missing[:2])} would strengthen your application")
    if not parts:
        return f"This role is a {score:.0f}% match based on your overall profile."
    return ". ".join(parts).capitalize() + "."


# ── CV Summary for Candidate view ──────────────────────────────────────────────

def summarise_profile(
    name: str, skills: List[str], exp: float,
    edu: Optional[str], matched_jobs_count: int,
) -> str:
    """One-paragraph profile summary shown to the candidate after CV upload."""
    client = _client()
    if not client:
        return (
            f"We detected {len(skills)} skills in your CV including "
            f"{', '.join(skills[:4])}{'...' if len(skills)>4 else ''}. "
            f"Based on your {exp} years of experience, "
            f"we found {matched_jobs_count} matching job{'s' if matched_jobs_count!=1 else ''} for you."
        )
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=160,
            messages=[{
                "role": "user",
                "content": f"""Write a 2-sentence encouraging profile summary for a job seeker (no greetings, no bullet points).
Name: {name} | Experience: {exp} yrs | Education: {edu or 'not specified'}
Skills: {', '.join(skills[:15])}
Matched jobs found: {matched_jobs_count}
Summary:""",
            }],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        logger.debug("Claude summary failed: %s", e)
        return (
            f"We detected {len(skills)} skills from your CV. "
            f"Found {matched_jobs_count} matching job{'s' if matched_jobs_count!=1 else ''} for you."
        )
