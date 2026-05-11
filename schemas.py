from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


# ── Skill ─────────────────────────────────────────────────────────────────────

class SkillBase(BaseModel):
    name: str

class SkillOut(SkillBase):
    id: int
    class Config:
        from_attributes = True


# ── Candidate ─────────────────────────────────────────────────────────────────

class CandidateBase(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    years_experience: float = 0.0
    education_level: Optional[str] = None
    education_field: Optional[str] = None

class CandidateOut(CandidateBase):
    id: int
    file_name: Optional[str] = None
    created_at: datetime
    skills: List[SkillOut] = []
    class Config:
        from_attributes = True


# ── Job Description ───────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title: str
    description: str
    min_experience: float = 0.0
    education_required: Optional[str] = None

class JobOut(JobCreate):
    id: int
    created_at: datetime
    required_skills: List[SkillOut] = []
    class Config:
        from_attributes = True


# ── Matching ──────────────────────────────────────────────────────────────────

class MatchResult(BaseModel):
    candidate: CandidateOut
    score: float                   # 0–100
    skill_score: float
    experience_score: float
    education_score: float
    matched_skills: List[str]
    missing_skills: List[str]
