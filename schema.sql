-- CV Matcher – PostgreSQL schema
-- 1. Create the database first (run as superuser):
--      createdb -U postgres cv_matcher
--    OR in psql:
--      CREATE DATABASE cv_matcher;
-- 2. Then apply this file:
--      psql -U postgres -d cv_matcher -f schema.sql

-- Skills vocabulary (shared across candidates and jobs)
CREATE TABLE IF NOT EXISTS skills (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);

-- Candidates
CREATE TABLE IF NOT EXISTS candidates (
    id               SERIAL PRIMARY KEY,
    full_name        VARCHAR(255) NOT NULL,
    email            VARCHAR(255) UNIQUE,
    phone            VARCHAR(50),
    years_experience NUMERIC(5,1) DEFAULT 0,
    education_level  VARCHAR(100),
    education_field  VARCHAR(255),
    raw_text         TEXT,
    file_name        VARCHAR(255),
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);

-- Many-to-many: candidate ↔ skill
CREATE TABLE IF NOT EXISTS candidate_skills (
    candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    skill_id     INTEGER NOT NULL REFERENCES skills(id)     ON DELETE CASCADE,
    PRIMARY KEY (candidate_id, skill_id)
);

-- Job descriptions
CREATE TABLE IF NOT EXISTS job_descriptions (
    id                 SERIAL PRIMARY KEY,
    title              VARCHAR(255) NOT NULL,
    description        TEXT         NOT NULL,
    min_experience     NUMERIC(5,1) DEFAULT 0,
    education_required VARCHAR(100),
    created_at         TIMESTAMPTZ  DEFAULT NOW()
);

-- Many-to-many: job_description ↔ skill (required skills)
CREATE TABLE IF NOT EXISTS job_skills (
    job_id   INTEGER NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id)           ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

-- Optional: pre-seed common skills
INSERT INTO skills (name) VALUES
  ('python'),('javascript'),('typescript'),('java'),('c++'),('go'),('rust'),
  ('react'),('vue'),('angular'),('nodejs'),('fastapi'),('flask'),('django'),
  ('postgresql'),('mysql'),('mongodb'),('redis'),('docker'),('kubernetes'),
  ('aws'),('azure'),('gcp'),('git'),('linux'),('rest api'),('graphql'),
  ('machine learning'),('deep learning'),('pandas'),('numpy'),('tensorflow'),
  ('pytorch'),('scikit-learn'),('sql'),('agile'),('scrum'),('ci/cd')
ON CONFLICT (name) DO NOTHING;
