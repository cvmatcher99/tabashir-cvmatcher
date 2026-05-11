from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SkillBase(BaseModel):
    name: str

class SkillOut(SkillBase):
    id: int
    class Config:
        from_attributes = True


class CandidateBase(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
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


class MatchResult(BaseModel):
    candidate: CandidateOut
    score: float
    skill_score: float
    experience_score: float
    education_score: float
    matched_skills: List[str]
    missing_skills: List[str]


class StatsOut(BaseModel):
    total_candidates: int
    total_jobs: int
    total_skills: int
    avg_experience: float
    top_skills: List[dict]
    recent_candidates: List[dict]
