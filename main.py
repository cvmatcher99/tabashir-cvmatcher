"""
CV Matcher – FastAPI application entry point.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Candidate, JobDescription, Skill, get_db, init_db
from matcher import extract_experience_from_text, extract_skills_from_text, match_candidates
from schemas import CandidateOut, JobCreate, JobOut, MatchResult
from cv_parser import parse_cv

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "cv_matcher.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE_MB = 10

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CV Matcher API",
    description="Upload CVs, store candidates, match to job descriptions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialised.")


# ── UI ─────────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>CV Matcher API</h1><p>Visit <a href='/docs'>/docs</a></p>")


# ── Helpers ────────────────────────────────────────────────────────────────────
def _get_or_create_skill(db: Session, name: str) -> Skill:
    name = name.lower().strip()
    skill = db.query(Skill).filter(Skill.name == name).first()
    if not skill:
        skill = Skill(name=name)
        db.add(skill)
        db.flush()
    return skill


# ── Candidates ────────────────────────────────────────────────────────────────
@app.post(
    "/candidates/upload",
    response_model=CandidateOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Candidates"],
    summary="Upload a CV file (PDF or DOCX)",
)
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type '{ext}' not supported. Use: {ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {MAX_FILE_SIZE_MB} MB limit.",
        )

    logger.info("Received CV upload: %s (%d bytes)", file.filename, len(content))

    # Save raw file
    save_path = UPLOAD_DIR / file.filename
    save_path.write_bytes(content)

    parsed = parse_cv(content, file.filename)

    # Deduplicate by email
    if parsed.get("email"):
        existing = db.query(Candidate).filter(Candidate.email == parsed["email"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Candidate with email '{parsed['email']}' already exists (id={existing.id}).",
            )

    candidate = Candidate(
        full_name=parsed.get("full_name") or "Unknown",
        email=parsed.get("email"),
        phone=parsed.get("phone"),
        years_experience=parsed.get("years_experience", 0.0),
        education_level=parsed.get("education_level"),
        education_field=parsed.get("education_field"),
        raw_text=parsed.get("raw_text", ""),
        file_name=file.filename,
    )
    db.add(candidate)
    db.flush()

    for skill_name in parsed.get("skills", []):
        if skill_name:
            candidate.skills.append(_get_or_create_skill(db, skill_name))

    db.commit()
    db.refresh(candidate)
    logger.info("Stored candidate id=%d name='%s'", candidate.id, candidate.full_name)
    return candidate


@app.get("/candidates", response_model=list[CandidateOut], tags=["Candidates"], summary="List all candidates")
def list_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Candidate).offset(skip).limit(limit).all()


@app.get("/candidates/{candidate_id}", response_model=CandidateOut, tags=["Candidates"])
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return cand


@app.delete("/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Candidates"])
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    db.delete(cand)
    db.commit()


# ── Job Descriptions ──────────────────────────────────────────────────────────
@app.post(
    "/jobs",
    response_model=JobOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Jobs"],
    summary="Submit a job description",
)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = JobDescription(
        title=payload.title,
        description=payload.description,
        min_experience=payload.min_experience,
        education_required=payload.education_required,
    )
    db.add(job)
    db.flush()

    # Auto-extract skills and experience from description text
    auto_skills = extract_skills_from_text(payload.description)
    if payload.min_experience == 0:
        job.min_experience = extract_experience_from_text(payload.description)

    for skill_name in auto_skills:
        job.required_skills.append(_get_or_create_skill(db, skill_name))

    db.commit()
    db.refresh(job)
    logger.info(
        "Created job id=%d title='%s' skills=%d",
        job.id, job.title, len(job.required_skills),
    )
    return job


@app.get("/jobs", response_model=list[JobOut], tags=["Jobs"], summary="List all job descriptions")
def list_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(JobDescription).offset(skip).limit(limit).all()


@app.get("/jobs/{job_id}", response_model=JobOut, tags=["Jobs"])
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@app.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Jobs"])
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    db.delete(job)
    db.commit()


# ── Matching ───────────────────────────────────────────────────────────────────
@app.get(
    "/jobs/{job_id}/matches",
    response_model=list[MatchResult],
    tags=["Matching"],
    summary="Get candidates matched to a job, sorted by relevance score",
)
def get_matches(job_id: int, top_k: int = 20, db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    results = match_candidates(job, db)
    logger.info("Matched job id=%d → %d candidates", job_id, len(results))
    return results[:top_k]


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "version": "1.0.0"}


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
