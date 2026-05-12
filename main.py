"""
CV Matcher – FastAPI application entry point.
"""
from __future__ import annotations

import csv
import io
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Candidate, JobDescription, Skill, candidate_skills as cs_table, get_db, init_db
from matcher import extract_experience_from_text, extract_skills_from_text, match_candidates, recommend_jobs
from schemas import CandidateOut, JobCreate, JobMatchResult, JobOut, MatchResult, StatsOut
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
STATIC_DIR = Path(__file__).parent / "static"


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialised.")
    yield


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CV Matcher API",
    description="Upload CVs, store candidates, match to job descriptions.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── UI ─────────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>CV Matcher API</h1><p>Visit <a href='/docs'>/docs</a></p>")


@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def admin_panel():
    html_path = STATIC_DIR / "admin.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Admin panel not found.</h1>", status_code=404)


# ── Admin Auth & Seed ─────────────────────────────────────────────────────────
from pydantic import BaseModel as _BaseModel

class _PasswordIn(_BaseModel):
    password: str


@app.post("/admin/verify", tags=["Admin"], summary="Verify admin password")
def admin_verify(payload: _PasswordIn):
    expected = os.getenv("ADMIN_PASSWORD", "admin1234")
    if payload.password != expected:
        raise HTTPException(status_code=401, detail="Incorrect password.")
    return {"ok": True}


@app.post("/admin/seed-jobs", tags=["Admin"], summary="Load 8 sample job descriptions")
def admin_seed_jobs(db: Session = Depends(get_db)):
    from seed_jobs import seed
    created = seed(db_session=db)
    msg = f"{created} sample job(s) added." if created else "All sample jobs already exist."
    logger.info("Seed jobs: %s", msg)
    return {"created": created, "message": msg}


# ── Helpers ────────────────────────────────────────────────────────────────────
def _get_or_create_skill(db: Session, name: str) -> Skill:
    name = name.lower().strip()
    skill = db.query(Skill).filter(Skill.name == name).first()
    if not skill:
        skill = Skill(name=name)
        db.add(skill)
        db.flush()
    return skill


# ── Stats ──────────────────────────────────────────────────────────────────────
@app.get("/stats", response_model=StatsOut, tags=["System"], summary="Dashboard statistics")
def get_stats(db: Session = Depends(get_db)):
    total_candidates = db.query(Candidate).count()
    total_jobs       = db.query(JobDescription).count()
    total_skills     = db.query(Skill).count()
    avg_exp_raw      = db.query(func.avg(Candidate.years_experience)).scalar()
    avg_exp          = round(float(avg_exp_raw), 1) if avg_exp_raw is not None else 0.0

    top_skills = (
        db.query(Skill.name, func.count(cs_table.c.candidate_id).label("cnt"))
        .join(cs_table, Skill.id == cs_table.c.skill_id)
        .group_by(Skill.name)
        .order_by(func.count(cs_table.c.candidate_id).desc())
        .limit(12)
        .all()
    )

    recent = (
        db.query(Candidate)
        .order_by(Candidate.created_at.desc())
        .limit(5)
        .all()
    )

    return StatsOut(
        total_candidates=total_candidates,
        total_jobs=total_jobs,
        total_skills=total_skills,
        avg_experience=avg_exp,
        top_skills=[{"name": s.name, "count": s.cnt} for s in top_skills],
        recent_candidates=[
            {"id": c.id, "name": c.full_name, "email": c.email or "",
             "skills": len(c.skills), "exp": c.years_experience}
            for c in recent
        ],
    )


# ── Skills ─────────────────────────────────────────────────────────────────────
@app.get("/skills", tags=["System"], summary="List all skills in the database")
def list_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).order_by(Skill.name).all()
    return [{"id": s.id, "name": s.name} for s in skills]


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
            status_code=422,
            detail=f"File type '{ext}' not supported. Use: {ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {MAX_FILE_SIZE_MB} MB.")

    logger.info("CV upload: %s (%d bytes)", file.filename, len(content))
    (UPLOAD_DIR / file.filename).write_bytes(content)

    parsed = parse_cv(content, file.filename)

    if parsed.get("email"):
        existing = db.query(Candidate).filter(Candidate.email == parsed["email"]).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Candidate with email '{parsed['email']}' already exists (id={existing.id}).",
            )

    candidate = Candidate(
        full_name=parsed.get("full_name") or "Unknown",
        email=parsed.get("email"),
        phone=parsed.get("phone"),
        location=parsed.get("location"),
        linkedin=parsed.get("linkedin"),
        github=parsed.get("github"),
        years_experience=parsed.get("years_experience", 0.0),
        education_level=parsed.get("education_level"),
        education_field=parsed.get("education_field"),
        raw_text=parsed.get("raw_text", ""),
        file_name=file.filename,
    )
    db.add(candidate)
    db.flush()

    seen_skills: set = set()
    for skill_name in parsed.get("skills", []):
        if skill_name:
            key = skill_name.lower().strip()
            if key in seen_skills:
                continue
            seen_skills.add(key)
            skill = _get_or_create_skill(db, key)
            if skill not in candidate.skills:
                candidate.skills.append(skill)

    db.commit()
    db.refresh(candidate)
    logger.info("Stored candidate id=%d name='%s'", candidate.id, candidate.full_name)
    return candidate


@app.get(
    "/candidates",
    response_model=list[CandidateOut],
    tags=["Candidates"],
    summary="List / search candidates",
)
def list_candidates(
    q: Optional[str] = Query(None, description="Search by name or email"),
    skill: Optional[str] = Query(None, description="Filter by skill name"),
    min_exp: float = Query(0, description="Minimum years of experience"),
    education: Optional[str] = Query(None, description="Filter by education level"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Candidate)
    if q:
        query = query.filter(
            Candidate.full_name.ilike(f"%{q}%") | Candidate.email.ilike(f"%{q}%")
        )
    if skill:
        query = query.join(Candidate.skills).filter(Skill.name.ilike(f"%{skill}%"))
    if min_exp > 0:
        query = query.filter(Candidate.years_experience >= min_exp)
    if education:
        query = query.filter(Candidate.education_level.ilike(f"%{education}%"))
    return query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()


@app.get("/candidates/{candidate_id}", response_model=CandidateOut, tags=["Candidates"])
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return cand


@app.delete("/candidates/{candidate_id}", status_code=204, tags=["Candidates"])
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    db.delete(cand)
    db.commit()


# ── Jobs ──────────────────────────────────────────────────────────────────────
@app.post("/jobs", response_model=JobOut, status_code=201, tags=["Jobs"], summary="Submit a job description")
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = JobDescription(
        title=payload.title,
        description=payload.description,
        min_experience=payload.min_experience,
        education_required=payload.education_required,
    )
    db.add(job)
    db.flush()

    auto_skills = extract_skills_from_text(payload.description)
    if payload.min_experience == 0:
        job.min_experience = extract_experience_from_text(payload.description)

    for skill_name in auto_skills:
        job.required_skills.append(_get_or_create_skill(db, skill_name))

    db.commit()
    db.refresh(job)
    logger.info("Job id=%d '%s' — %d skills extracted", job.id, job.title, len(job.required_skills))
    return job


@app.get("/jobs", response_model=list[JobOut], tags=["Jobs"])
def list_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(JobDescription).order_by(JobDescription.created_at.desc()).offset(skip).limit(limit).all()


@app.get("/jobs/{job_id}", response_model=JobOut, tags=["Jobs"])
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@app.delete("/jobs/{job_id}", status_code=204, tags=["Jobs"])
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    db.delete(job)
    db.commit()


# ── Matching ──────────────────────────────────────────────────────────────────
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


@app.get(
    "/jobs/{job_id}/matches/export",
    tags=["Matching"],
    summary="Export matched candidates as CSV",
)
def export_matches_csv(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    results = match_candidates(job, db)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Name", "Email", "Location", "Score (%)",
        "Skill Score", "Experience Score", "Education Score",
        "Matched Skills", "Missing Skills", "Experience (yrs)", "Education",
        "LinkedIn", "GitHub",
    ])
    for i, r in enumerate(results, 1):
        c = r.candidate
        writer.writerow([
            i, c.full_name, c.email or "", c.location or "",
            r.score, r.skill_score, r.experience_score, r.education_score,
            ", ".join(r.matched_skills), ", ".join(r.missing_skills),
            c.years_experience, c.education_level or "",
            c.linkedin or "", c.github or "",
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=matches_job_{job_id}.csv"},
    )


# ── Job Recommendations for Candidate ────────────────────────────────────────
@app.get(
    "/candidates/{candidate_id}/recommend-jobs",
    response_model=list[JobMatchResult],
    tags=["Matching"],
    summary="Recommend best-matching jobs for a candidate",
)
def get_job_recommendations(candidate_id: int, top_k: int = 10, db: Session = Depends(get_db)):
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    results = recommend_jobs(cand, db)
    logger.info("Recommended %d jobs for candidate id=%d", len(results), candidate_id)
    return results[:top_k]


@app.post(
    "/find-jobs",
    response_model=list[JobMatchResult],
    status_code=200,
    tags=["Matching"],
    summary="Upload a CV and instantly get matching job recommendations",
)
async def find_jobs_for_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    One-shot endpoint for candidates: upload your CV → get ranked job list.
    Does NOT store the candidate permanently unless email is new.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {MAX_FILE_SIZE_MB} MB.")

    parsed = parse_cv(content, file.filename)

    # Reuse existing candidate if email matches, else create temp object
    cand = None
    if parsed.get("email"):
        cand = db.query(Candidate).filter(Candidate.email == parsed["email"]).first()

    if not cand:
        cand = Candidate(
            full_name=parsed.get("full_name") or "Candidate",
            email=parsed.get("email"),
            phone=parsed.get("phone"),
            location=parsed.get("location"),
            linkedin=parsed.get("linkedin"),
            github=parsed.get("github"),
            years_experience=parsed.get("years_experience", 0.0),
            education_level=parsed.get("education_level"),
            education_field=parsed.get("education_field"),
            raw_text=parsed.get("raw_text", ""),
            file_name=file.filename,
        )
        db.add(cand)
        db.flush()
        seen_skills: set = set()
        for skill_name in parsed.get("skills", []):
            if skill_name:
                key = skill_name.lower().strip()
                if key in seen_skills:
                    continue
                seen_skills.add(key)
                skill = db.query(Skill).filter(Skill.name == key).first()
                if not skill:
                    skill = Skill(name=key)
                    db.add(skill)
                    db.flush()
                if skill not in cand.skills:
                    cand.skills.append(skill)
        db.commit()
        db.refresh(cand)

    results = recommend_jobs(cand, db)
    logger.info("find-jobs: %d recommendations for '%s'", len(results), cand.full_name)
    return results[:10]


# ── Career Coach ──────────────────────────────────────────────────────────────
@app.post(
    "/career-coach",
    tags=["Career Coach"],
    summary="Generate a premium career development report for a candidate",
)
async def career_coach(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a CV and receive a full career coaching report:
    strengths, skill gaps with real course links, action plan, and career roadmap.
    Covers office/admin, engineering, and medical fields — UAE market focused.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {MAX_FILE_SIZE_MB} MB.")

    parsed = parse_cv(content, file.filename)

    from ai_service import career_coach_analysis
    report = career_coach_analysis(
        name=parsed.get("full_name") or "Candidate",
        skills=parsed.get("skills") or [],
        exp=parsed.get("years_experience") or 0.0,
        edu=parsed.get("education_level"),
        edu_field=parsed.get("education_field"),
        raw_text=parsed.get("raw_text") or "",
    )

    if not report:
        raise HTTPException(status_code=500, detail="Could not generate career report.")

    logger.info("Career coach report generated for '%s'", parsed.get("full_name"))
    return report


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
