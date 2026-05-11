"""
AI integration — CV parsing + job match explanations.
Primary: Groq (free, fast LLaMA). Fallback: regex/template.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.1-8b-instant"


def _groq_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=key)
    except ImportError:
        logger.warning("groq package not installed. Run: pip install groq")
        return None
    except Exception as e:
        logger.warning("Groq init failed: %s", e)
        return None


def _generate(prompt: str, max_tokens: int = 800) -> Optional[str]:
    client = _groq_client()
    if not client:
        return None
    try:
        r = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.1,
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("Groq generation failed: %s", e)
        return None


# ── CV Parsing ─────────────────────────────────────────────────────────────────

def parse_cv_claude(text: str) -> Optional[Dict[str, Any]]:
    """Extract structured candidate data from raw CV text using AI."""
    prompt = f"""Extract structured information from this CV. Return ONLY valid JSON with these exact keys:
full_name, email, phone, linkedin (URL or null), github (URL or null),
location (city/country or null), years_experience (number),
education_level (one of: PhD, Master, Bachelor, Associate, High School, or null),
education_field (string or null), skills (array of lowercase tech/professional skill strings).

CV TEXT:
\"\"\"
{text[:5000]}
\"\"\"

Return ONLY the JSON object, no explanation, no markdown:"""

    raw = _generate(prompt, max_tokens=1024)
    if not raw:
        return None
    try:
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        # Extract JSON object if surrounded by other text
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            raw = m.group(0)
        data = json.loads(raw)
        data["years_experience"] = float(data.get("years_experience") or 0)
        data["skills"] = [s.lower().strip() for s in (data.get("skills") or [])]
        logger.info("Groq parsed CV: %s, %d skills", data.get("full_name"), len(data["skills"]))
        return data
    except Exception as e:
        logger.warning("Groq CV parse JSON error: %s | raw: %s", e, raw[:200])
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
    prompt = f"""Write exactly 2 short sentences (max 50 words total) explaining why this job is a {score:.0f}% match.
Be specific and mention actual skills. No bullet points. No greetings.

Candidate: {candidate_name} | {candidate_exp} yrs | {candidate_edu or 'unspecified'}
Job: {job_title} | {min_exp}+ yrs required
Matched skills: {', '.join(matched[:5]) or 'none'}
Missing skills: {', '.join(missing[:3]) or 'none'}

2 sentences only:"""

    result = _generate(prompt, max_tokens=100)
    if result:
        return result
    return _fallback_explanation(candidate_exp, min_exp, matched, missing, score)


def _fallback_explanation(
    candidate_exp: float, min_exp: float,
    matched: List[str], missing: List[str], score: float,
) -> str:
    parts = []
    if matched:
        parts.append(f"Your skills in {', '.join(matched[:3])} align well with this role")
    if candidate_exp >= (min_exp or 0):
        parts.append("your experience meets the requirement")
    elif min_exp > 0:
        parts.append(f"consider building more experience to meet the {min_exp}-year requirement")
    if missing:
        parts.append(f"adding {', '.join(missing[:2])} would strengthen your application")
    if not parts:
        return f"This role is a {score:.0f}% match based on your overall profile."
    return ". ".join(parts).capitalize() + "."


# ── Profile Summary ────────────────────────────────────────────────────────────

def summarise_profile(
    name: str, skills: List[str], exp: float,
    edu: Optional[str], matched_jobs_count: int,
) -> str:
    prompt = f"""Write 2 short encouraging sentences for a job seeker profile. No greetings, no bullet points.
Name: {name} | Experience: {exp} yrs | Education: {edu or 'not specified'}
Top skills: {', '.join(skills[:10])}
Matching jobs found: {matched_jobs_count}
2 sentences:"""

    result = _generate(prompt, max_tokens=120)
    if result:
        return result
    return (
        f"We detected {len(skills)} skills in your CV including "
        f"{', '.join(skills[:4])}{'...' if len(skills) > 4 else ''}. "
        f"Found {matched_jobs_count} matching job{'s' if matched_jobs_count != 1 else ''} for you."
    )
