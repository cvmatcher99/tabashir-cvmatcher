import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text,
    DateTime, ForeignKey, Table
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:password@localhost:5432/cv_matcher"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Association table: candidate ↔ skill
candidate_skills = Table(
    "candidate_skills",
    Base.metadata,
    Column("candidate_id", Integer, ForeignKey("candidates.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id",     Integer, ForeignKey("skills.id",      ondelete="CASCADE"), primary_key=True),
)

# Association table: job_description ↔ skill
job_skills = Table(
    "job_skills",
    Base.metadata,
    Column("job_id",   Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id",           ondelete="CASCADE"), primary_key=True),
)


class Candidate(Base):
    __tablename__ = "candidates"

    id               = Column(Integer, primary_key=True, index=True)
    full_name        = Column(String(255), nullable=False)
    email            = Column(String(255), unique=True, index=True)
    phone            = Column(String(50))
    years_experience = Column(Float, default=0.0)
    education_level  = Column(String(100))   # e.g. "Bachelor", "Master", "PhD", "High School"
    education_field  = Column(String(255))
    raw_text         = Column(Text)
    file_name        = Column(String(255))
    created_at       = Column(DateTime, default=datetime.utcnow)

    skills = relationship("Skill", secondary=candidate_skills, back_populates="candidates")


class Skill(Base):
    __tablename__ = "skills"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    candidates = relationship("Candidate", secondary=candidate_skills, back_populates="skills")
    job_descriptions = relationship("JobDescription", secondary=job_skills, back_populates="required_skills")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id                 = Column(Integer, primary_key=True, index=True)
    title              = Column(String(255), nullable=False)
    description        = Column(Text, nullable=False)
    min_experience     = Column(Float, default=0.0)
    education_required = Column(String(100))
    created_at         = Column(DateTime, default=datetime.utcnow)

    required_skills = relationship("Skill", secondary=job_skills, back_populates="job_descriptions")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
