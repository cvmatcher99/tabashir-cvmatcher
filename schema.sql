-- =============================================================================
-- CV Matcher — PostgreSQL Schema
-- =============================================================================
-- Run this file to create all tables from scratch:
--   psql -U postgres -d cv_matcher -f schema.sql
-- =============================================================================

-- Drop tables in reverse-dependency order (safe re-run)
DROP TABLE IF EXISTS candidate_skills  CASCADE;
DROP TABLE IF EXISTS job_skills        CASCADE;
DROP TABLE IF EXISTS candidates        CASCADE;
DROP TABLE IF EXISTS skills            CASCADE;
DROP TABLE IF EXISTS job_descriptions  CASCADE;

-- -----------------------------------------------------------------------------
-- skills
-- Central skill vocabulary shared by candidates and job descriptions.
-- -----------------------------------------------------------------------------
CREATE TABLE skills (
    id   SERIAL       PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE INDEX idx_skills_name ON skills(name);

-- -----------------------------------------------------------------------------
-- candidates
-- One row per uploaded CV.
-- -----------------------------------------------------------------------------
CREATE TABLE candidates (
    id               SERIAL       PRIMARY KEY,
    full_name        VARCHAR(255) NOT NULL,
    email            VARCHAR(255) UNIQUE,
    phone            VARCHAR(50),
    location         VARCHAR(255),
    linkedin         VARCHAR(255),
    github           VARCHAR(255),
    years_experience FLOAT        NOT NULL DEFAULT 0.0,
    education_level  VARCHAR(100),          -- PhD | Master | Bachelor | Diploma | High School
    education_field  VARCHAR(255),          -- e.g. "Computer Science"
    raw_text         TEXT,                  -- full extracted CV text (for re-parsing)
    file_name        VARCHAR(255),
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_candidates_email      ON candidates(email);
CREATE INDEX idx_candidates_exp        ON candidates(years_experience DESC);
CREATE INDEX idx_candidates_created_at ON candidates(created_at DESC);

-- -----------------------------------------------------------------------------
-- job_descriptions
-- Each row is one job posting entered by HR.
-- -----------------------------------------------------------------------------
CREATE TABLE job_descriptions (
    id                 SERIAL       PRIMARY KEY,
    title              VARCHAR(255) NOT NULL,
    description        TEXT         NOT NULL,
    min_experience     FLOAT        NOT NULL DEFAULT 0.0,
    education_required VARCHAR(100),          -- minimum education level required
    created_at         TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_jobs_created_at ON job_descriptions(created_at DESC);

-- -----------------------------------------------------------------------------
-- candidate_skills  (many-to-many)
-- Links candidates to the skills extracted from their CVs.
-- -----------------------------------------------------------------------------
CREATE TABLE candidate_skills (
    candidate_id INTEGER NOT NULL REFERENCES candidates(id)       ON DELETE CASCADE,
    skill_id     INTEGER NOT NULL REFERENCES skills(id)           ON DELETE CASCADE,
    PRIMARY KEY (candidate_id, skill_id)
);

-- -----------------------------------------------------------------------------
-- job_skills  (many-to-many)
-- Links job descriptions to the skills they require.
-- -----------------------------------------------------------------------------
CREATE TABLE job_skills (
    job_id   INTEGER NOT NULL REFERENCES job_descriptions(id)    ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id)              ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

-- =============================================================================
-- Useful example queries
-- =============================================================================

-- Top 10 most common skills across all candidates:
-- SELECT s.name, COUNT(*) AS cnt
-- FROM skills s
-- JOIN candidate_skills cs ON s.id = cs.skill_id
-- GROUP BY s.name ORDER BY cnt DESC LIMIT 10;

-- Find candidates matching a specific skill:
-- SELECT c.full_name, c.email, c.years_experience, c.education_level
-- FROM candidates c
-- JOIN candidate_skills cs ON c.id = cs.candidate_id
-- JOIN skills s ON cs.skill_id = s.id
-- WHERE s.name = 'python'
-- ORDER BY c.years_experience DESC;

-- Jobs with required skill count:
-- SELECT j.title, j.min_experience, COUNT(js.skill_id) AS required_skills
-- FROM job_descriptions j
-- LEFT JOIN job_skills js ON j.id = js.job_id
-- GROUP BY j.id, j.title, j.min_experience
-- ORDER BY required_skills DESC;

-- Candidate skill overlap with a job (manual match preview):
-- SELECT c.full_name,
--        COUNT(DISTINCT cs.skill_id) FILTER (WHERE cs.skill_id IN (
--            SELECT skill_id FROM job_skills WHERE job_id = 1
--        )) AS matched,
--        COUNT(DISTINCT js.skill_id) AS total_required
-- FROM candidates c
-- JOIN candidate_skills cs ON c.id = cs.candidate_id
-- CROSS JOIN (SELECT skill_id FROM job_skills WHERE job_id = 1) js
-- GROUP BY c.id, c.full_name
-- ORDER BY matched DESC;
