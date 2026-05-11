# CV Matcher

A Python system that **parses CVs**, stores candidate data in **PostgreSQL**, and **matches candidates to job descriptions** via a scored ranking algorithm.

Built with FastAPI · SQLAlchemy · pdfplumber · python-docx · optional OpenAI integration.

---

## Features

| Feature | Details |
|---------|---------|
| CV Upload | PDF and DOCX support, drag-and-drop UI |
| Extraction | Name, email, phone, skills, experience, education |
| Storage | PostgreSQL with normalised schema |
| Job Matching | Weighted score: skills (55%) + experience (30%) + education (15%) |
| OpenAI Boost | GPT-powered parsing + embedding-based semantic skill matching (optional) |
| REST API | Full CRUD + matching endpoints, auto docs at `/docs` |
| Web UI | Single-page app served from `/` |
| Logging | Structured logs to `logs/cv_matcher.log` |
| Packaging | PyInstaller `.exe` for Windows |

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+ running locally (or remote)

### 2. Clone & Install

```bash
git clone <repo-url>
cd cv_matcher
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env – set DATABASE_URL (and optionally OPENAI_API_KEY)
```

`.env` example:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/cv_matcher
PORT=8000
# OPENAI_API_KEY=sk-...
```

### 4. Create the database

```bash
# In psql:
CREATE DATABASE cv_matcher;

# Then apply schema (optional – SQLAlchemy auto-creates tables on startup):
psql -U postgres -d cv_matcher -f schema.sql
```

### 5. Run

```bash
python main.py
```

Open **http://localhost:8000** for the web UI.  
API docs: **http://localhost:8000/docs**

### 6. Generate sample CVs

```bash
pip install python-docx   # if not already installed
python create_samples.py
# Creates 4 DOCX CVs in ./sample_cvs/
```

---

## API Reference

### Candidates

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/candidates/upload` | Upload CV file (form-data `file`) |
| `GET`  | `/candidates` | List all candidates |
| `GET`  | `/candidates/{id}` | Get candidate by ID |
| `DELETE` | `/candidates/{id}` | Delete candidate |

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/jobs` | Create job description (JSON) |
| `GET`  | `/jobs` | List all jobs |
| `GET`  | `/jobs/{id}` | Get job by ID |
| `DELETE` | `/jobs/{id}` | Delete job |

### Matching

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/jobs/{id}/matches` | Get ranked candidates for a job |

**Match response fields:**
```json
{
  "candidate": { ... },
  "score": 87.5,
  "skill_score": 90.0,
  "experience_score": 85.0,
  "education_score": 75.0,
  "matched_skills": ["python", "fastapi", "docker"],
  "missing_skills": ["kubernetes"]
}
```

---

## Scoring Algorithm

```
total = (skill_score × 0.55) + (exp_score × 0.30) + (edu_score × 0.15)
      + semantic_boost (0–20, OpenAI embeddings, optional)

skill_score     = (matched_skills / required_skills) × 100
exp_score       = min(candidate_exp / required_exp, 1.5) × 90  (capped at 100)
edu_score       = 100 if candidate meets or exceeds required level, else −25 per level short
```

---

## OpenAI Integration

Set `OPENAI_API_KEY` in `.env` to enable:

1. **CV Parsing** – GPT-4o-mini extracts structured fields (more accurate than regex for complex CVs).
2. **Semantic Matching** – `text-embedding-3-small` adds up to +20 score points via cosine similarity between candidate and job skill sets.

---

## Database Schema

```
skills            id, name
candidates        id, full_name, email, phone, years_experience,
                  education_level, education_field, raw_text, file_name
candidate_skills  candidate_id → candidates, skill_id → skills
job_descriptions  id, title, description, min_experience, education_required
job_skills        job_id → job_descriptions, skill_id → skills
```

---

## Building the Executable

### Requirements

```bash
pip install pyinstaller
```

### Build

```bash
pyinstaller cv_matcher.spec
```

Output: `dist/cv_matcher/cv_matcher.exe`

### Running the Executable

1. Copy the entire `dist/cv_matcher/` folder to the target Windows machine.
2. Edit (or create) `.env` inside that folder.
3. Double-click `cv_matcher.exe` **or** run from a terminal:

```cmd
cd dist\cv_matcher
cv_matcher.exe
```

4. Open **http://localhost:8000** in a browser.

> **Note:** PostgreSQL must be accessible from the target machine. The executable does **not** bundle PostgreSQL itself.

### Requirements on the target machine

- Windows 10/11 (64-bit)
- PostgreSQL server (local or remote, accessible via the `DATABASE_URL` in `.env`)
- No Python installation required

---

## Project Structure

```
cv_matcher/
├── main.py            # FastAPI app + all endpoints
├── database.py        # SQLAlchemy models & DB init
├── schemas.py         # Pydantic request/response models
├── cv_parser.py       # PDF/DOCX text extraction & field parsing
├── matcher.py         # Scoring & ranking algorithm
├── run.py             # PyInstaller entry point
├── cv_matcher.spec    # PyInstaller build spec
├── create_samples.py  # Generate sample DOCX CVs
├── requirements.txt
├── schema.sql         # Raw SQL schema
├── .env.example       # Environment variable template
├── static/
│   └── index.html     # Single-page web UI
├── uploads/           # Uploaded CV files (auto-created)
└── logs/              # Application logs (auto-created)
```

---

## Development

```bash
# Run with hot reload
uvicorn main:app --reload --port 8000

# Run tests (if added)
pytest
```

---

## License

MIT
