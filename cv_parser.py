"""
CV parsing: extract structured fields from PDF / DOCX files.
Falls back to regex heuristics; uses OpenAI when OPENAI_API_KEY is set.
"""
from __future__ import annotations

import io
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

KNOWN_SKILLS: List[str] = [
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "bash",
    "shell", "powershell", "vba", "dart", "lua",
    "html", "css", "react", "angular", "vue", "nextjs", "nuxtjs", "svelte",
    "jquery", "bootstrap", "tailwind", "sass", "less", "webpack", "vite",
    "node.js", "nodejs", "express", "fastapi", "flask", "django", "rails",
    "spring", "spring boot", "laravel", "asp.net", ".net",
    "sql", "nosql", "pandas", "numpy", "scikit-learn", "tensorflow", "keras",
    "pytorch", "hugging face", "transformers", "nlp", "computer vision",
    "deep learning", "machine learning", "data science", "data analysis",
    "matplotlib", "seaborn", "plotly", "tableau", "power bi", "excel",
    "spark", "hadoop", "kafka", "airflow", "dbt", "etl",
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "oracle", "mssql", "firebase",
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "ansible", "jenkins", "github actions", "gitlab ci", "circleci", "linux",
    "nginx", "apache", "heroku", "vercel", "netlify",
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack",
    "figma", "postman", "swagger", "graphql", "rest api", "soap", "grpc",
    "microservices", "agile", "scrum", "kanban", "tdd", "ci/cd",
    "openai", "langchain", "llm", "prompt engineering",
]

EDUCATION_LEVELS = {
    "phd": 4, "doctorate": 4,
    "master": 3, "msc": 3, "mba": 3, "m.s.": 3, "m.sc": 3,
    "bachelor": 2, "bsc": 2, "b.s.": 2, "b.sc": 2, "undergraduate": 2,
    "associate": 1, "diploma": 1, "certificate": 1,
    "high school": 0, "secondary": 0,
}


def extract_text_from_pdf(content: bytes) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as exc:
        logger.error("PDF extraction failed: %s", exc)
        return ""


def extract_text_from_docx(content: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as exc:
        logger.error("DOCX extraction failed: %s", exc)
        return ""


def extract_text(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(content)
    if ext in (".docx", ".doc"):
        return extract_text_from_docx(content)
    return content.decode("utf-8", errors="ignore")


def _extract_email(text: str) -> Optional[str]:
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0).lower() if m else None


def _extract_phone(text: str) -> Optional[str]:
    m = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", text)
    return m.group(0).strip() if m else None


def _extract_linkedin(text: str) -> Optional[str]:
    m = re.search(r"linkedin\.com/in/[\w\-]+", text, re.I)
    return m.group(0) if m else None


def _extract_github(text: str) -> Optional[str]:
    m = re.search(r"github\.com/[\w\-]+", text, re.I)
    return m.group(0) if m else None


def _extract_location(text: str) -> Optional[str]:
    patterns = [
        r"(?:location|address|city|based in)[:\s]+([A-Za-z\s,]+?)(?:\n|,\s*[A-Z]{2}|\|)",
        r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Za-z]+)\b",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            loc = m.group(1).strip()
            if 2 < len(loc) < 60 and not re.search(r"(university|college|school|institute)", loc, re.I):
                return loc
    return None


def _extract_name(text: str, email: Optional[str]) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in lines[:6]:
        if re.search(r"[@|]|https?://|linkedin|github|\d{5,}", line, re.I):
            continue
        if re.search(r"[a-zA-Z]{2,}", line) and len(line.split()) <= 5:
            if not re.search(r"(resume|curriculum|vitae|cv|profile|summary|objective)", line, re.I):
                return line
    return "Unknown"


def _extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    return [s for s in KNOWN_SKILLS if re.search(r"\b" + re.escape(s) + r"\b", text_lower)]


def _extract_experience(text: str) -> float:
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?(?:work\s+)?experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"(\d+(?:\.\d+)?)\s*\+?\s*yrs?\s+(?:of\s+)?experience",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            return float(m.group(1))

    from datetime import date
    current_year = date.today().year
    ranges = re.findall(
        r"\b(20\d{2}|19\d{2})\b\s*[-–—to]+\s*\b(20\d{2}|present|now|current)\b",
        text, re.I
    )
    total = 0.0
    for start, end in ranges:
        try:
            s = int(start)
            e = current_year if end.lower() in ("present", "now", "current") else int(end)
            if 1970 < s <= current_year and s <= e:
                total += e - s
        except ValueError:
            pass
    return round(min(total, 50.0), 1)


def _extract_education(text: str):
    text_lower = text.lower()
    best_level, best_rank, best_field = None, -1, None
    for keyword, rank in EDUCATION_LEVELS.items():
        if keyword in text_lower and rank > best_rank:
            best_rank = rank
            best_level = keyword.title()
            idx = text_lower.find(keyword)
            snippet = text[max(0, idx - 30): idx + 120]
            field_m = re.search(
                r"(?:in|of)\s+([A-Za-z\s&]+?)(?:\n|,|\.|\(|from|at|university|college)", snippet, re.I
            )
            if field_m:
                best_field = field_m.group(1).strip()
    return best_level, best_field


def _regex_parse(text: str) -> Dict[str, Any]:
    email = _extract_email(text)
    edu_level, edu_field = _extract_education(text)
    return {
        "full_name":        _extract_name(text, email),
        "email":            email,
        "phone":            _extract_phone(text),
        "linkedin":         _extract_linkedin(text),
        "github":           _extract_github(text),
        "location":         _extract_location(text),
        "skills":           _extract_skills(text),
        "years_experience": _extract_experience(text),
        "education_level":  edu_level,
        "education_field":  edu_field,
    }


def _claude_parse(text: str) -> Optional[Dict[str, Any]]:
    from ai_service import parse_cv_claude
    return parse_cv_claude(text)


def _openai_parse(text: str) -> Optional[Dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        skills_hint = ", ".join(KNOWN_SKILLS[:60])
        prompt = f"""Extract structured information from the CV text below.
Return ONLY valid JSON with these exact keys:
  full_name, email, phone, linkedin (URL or null), github (URL or null),
  location (city/country or null), years_experience (number),
  education_level (one of: PhD, Master, Bachelor, Associate, High School, or null),
  education_field (string or null), skills (array of lowercase strings).

For skills, use only well-known technical/professional skills (examples: {skills_hint}).

CV TEXT:
\"\"\"
{text[:6000]}
\"\"\"

JSON:"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0, max_tokens=800,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
        data["years_experience"] = float(data.get("years_experience") or 0)
        data["skills"] = [s.lower().strip() for s in (data.get("skills") or [])]
        return data
    except Exception as exc:
        logger.warning("OpenAI parsing failed, falling back to regex: %s", exc)
        return None


def parse_cv(content: bytes, filename: str) -> Dict[str, Any]:
    raw_text = extract_text(content, filename)
    if not raw_text.strip():
        logger.warning("No text extracted from %s", filename)
        return {
            "full_name": "Unknown", "email": None, "phone": None,
            "linkedin": None, "github": None, "location": None,
            "skills": [], "years_experience": 0.0,
            "education_level": None, "education_field": None, "raw_text": "",
        }
    parsed = _claude_parse(raw_text) or _openai_parse(raw_text) or _regex_parse(raw_text)
    parsed["raw_text"] = raw_text
    logger.info(
        "Parsed '%s': name=%s skills=%d exp=%.1f yrs",
        filename, parsed.get("full_name"), len(parsed.get("skills", [])),
        parsed.get("years_experience", 0),
    )
    return parsed
