# CV Matcher

A full-stack Python system that **parses CVs (PDF/DOCX)**, stores candidate data in **PostgreSQL**, and **matches candidates to job descriptions** using a weighted AI-powered scoring algorithm.

Built with **FastAPI · SQLAlchemy · Groq AI (LLaMA) · pdfplumber · python-docx**

---

## Features

| Feature | Details |
|---|---|
| CV Parsing | PDF & DOCX — extracts name, email, phone, skills, education, years of experience |
| AI Extraction | Groq (free LLaMA model) — accurate parsing for tech and non-tech CVs |
| Job Matching | Weighted score: Skills 55% · Experience 30% · Education 15% |
| REST API | FastAPI with auto-generated `/docs` (Swagger UI) |
| Admin Panel | Password-protected HR dashboard — manage candidates, jobs, matches, applications |
| Customer UI | Candidates upload CV and instantly see matching jobs |
| Google Sign-In | OAuth 2.0 — premium features require authentication |
| Apply for Job | Candidates apply directly; opens WhatsApp/email with pre-filled message |
| Career Coach | AI-generated career development report with skill gaps and action plan |
| CV Score | Rates a CV out of 100 with section-by-section breakdown and improvement tips |
| Interview Prep | Generates tailored interview questions matched to a specific job |
| Salary Estimator | Estimates monthly salary range in AED based on UAE 2025–2026 market benchmarks |
| Export | Download matched candidates as CSV |
| Logging | Rotating log files in `logs/cv_matcher.log` |

---

## Live Demo

> Deployed on Railway:  
> **https://cv-matcher-production.up.railway.app**

---

## Quick Start (Development)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Free Groq API key → [console.groq.com](https://console.groq.com)

### 2. Clone & install
```bash
git clone https://github.com/admin1191029/cv-matcher.git
cd cv-matcher
pip install -r requirements.txt
```

### 3. Create the database
```bash
# Create database
createdb -U postgres cv_matcher

# Apply schema
psql -U postgres -d cv_matcher -f schema.sql
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in:
#   DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/cv_matcher
#   GROQ_API_KEY=gsk_...
#   ADMIN_PASSWORD=your_password
```

### 5. Run the server
```bash
python -m uvicorn main:app --reload --port 8000
```

Open:
- **Customer UI** → http://localhost:8000
- **Admin Panel** → http://localhost:8000/admin
- **API Docs**    → http://localhost:8000/docs

### 6. Seed sample jobs (optional)
```bash
python seed_jobs.py
# or via API:
curl -X POST http://localhost:8000/admin/seed-jobs
```

### 7. Bulk upload sample CVs (optional)
```bash
python bulk_upload_cvs.py ./sample_cvs
```

---

## Running the Executable (.exe)

> For Windows users who don't have Python installed.

### Steps
1. Download `cv_matcher.exe` from the [Releases](https://github.com/admin1191029/cv-matcher/releases) page  
   (or find it in `dist/cv_matcher/` after building)
2. Place the entire `cv_matcher/` folder anywhere on your PC
3. Create a `.env` file next to `cv_matcher.exe`:
```
DATABASE_URL=postgresql+psycopg://postgres:PASSWORD@localhost:5432/cv_matcher
GROQ_API_KEY=gsk_...
ADMIN_PASSWORD=admin1234
PORT=8000
```
4. Double-click `cv_matcher.exe` or run from terminal:
```cmd
cv_matcher.exe
```
5. Open your browser → **http://localhost:8000**

> **Note:** PostgreSQL must be installed and running on the machine. The app connects to it via `DATABASE_URL`.

### Build the .exe yourself
```bash
pip install pyinstaller
pyinstaller cv_matcher.spec --clean --noconfirm
# Output: dist/cv_matcher/cv_matcher.exe
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/candidates/upload` | Upload a CV file (PDF/DOCX) |
| `GET`  | `/candidates` | List all candidates (supports filtering) |
| `GET`  | `/candidates/{id}` | Get single candidate |
| `DELETE` | `/candidates/{id}` | Delete candidate |
| `POST` | `/jobs` | Create a job description |
| `GET`  | `/jobs` | List all jobs |
| `GET`  | `/jobs/{id}/matches` | Get matched candidates sorted by score |
| `GET`  | `/jobs/{id}/matches/export` | Export matches as CSV |
| `POST` | `/find-jobs` | Upload CV → instantly get matching jobs |
| `POST` | `/apply` | Submit a job application |
| `GET`  | `/applications` | List all applications (admin) |
| `PATCH`| `/applications/{id}/status` | Update application status |
| `POST` | `/career-coach` | Generate AI career coaching report |
| `POST` | `/cv-score` | Score a CV out of 100 |
| `POST` | `/interview-prep` | Generate tailored interview questions |
| `POST` | `/salary-estimate` | Estimate salary range in AED |
| `GET`  | `/config` | Get public client-side config |
| `POST` | `/admin/seed-jobs` | Load sample job descriptions |
| `POST` | `/admin/verify` | Verify admin password |
| `GET`  | `/stats` | Dashboard statistics |
| `GET`  | `/health` | Health check |

Full interactive docs: **http://localhost:8000/docs**

---

## Database Schema

```
candidates          skills              job_descriptions
──────────────      ──────────────      ──────────────────
id (PK)             id (PK)             id (PK)
full_name           name (unique)       title
email (unique)                          description
phone               candidate_skills    min_experience
location            ──────────────      education_required
linkedin            candidate_id (FK)   created_at
github              skill_id (FK)
years_experience                        job_skills
education_level                         ──────────────
education_field                         job_id (FK)
raw_text                                skill_id (FK)
file_name
created_at
```

See [`schema.sql`](schema.sql) for the full PostgreSQL DDL.

---

## Matching Algorithm

```python
score = (skill_score * 0.55) + (experience_score * 0.30) + (education_score * 0.15)
```

| Component | How it's calculated |
|---|---|
| **Skill Score** | `matched_skills / total_required_skills` |
| **Experience Score** | `min(candidate_exp / required_exp, 1.0)` |
| **Education Score** | Level comparison (PhD=5, Master=4, Bachelor=3, Diploma=2, High School=1) |

Each match also includes an **AI-generated explanation** (Groq) describing why the candidate fits the role.

---

## Project Structure

```
cv_matcher/
├── main.py            # FastAPI app — all endpoints
├── database.py        # SQLAlchemy models & DB connection
├── cv_parser.py       # PDF/DOCX text extraction + field parsing
├── ai_service.py      # Groq AI integration (CV parsing + explanations)
├── matcher.py         # Weighted scoring & ranking logic
├── schemas.py         # Pydantic request/response models
├── seed_jobs.py       # 26 sample job descriptions
├── bulk_upload_cvs.py # Batch CV upload utility
├── run.py             # PyInstaller entry point
├── schema.sql         # PostgreSQL DDL
├── cv_matcher.spec    # PyInstaller build spec
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
├── Procfile           # Railway deployment
├── railway.json       # Railway config
├── static/
│   ├── index.html     # Customer-facing UI
│   └── admin.html     # Admin HR dashboard
└── logs/
    └── cv_matcher.log # Application logs
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | FastAPI 0.115 |
| Database ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 14+ |
| DB Driver | psycopg 3 |
| CV Parsing | pdfplumber · python-docx |
| AI | Groq API (LLaMA 3.1 8B) — free tier |
| Packaging | PyInstaller 6 |
| Deployment | Railway + Neon PostgreSQL |
| Frontend | Vanilla HTML/CSS/JS (dark theme, mobile responsive) |

---

## Sample CVs

Sample CVs are included in `sample_cvs/` for testing.  
Covers diverse profiles: software engineers, finance managers, HR officers, HVAC technicians, media professionals, customer service, operations managers, and more.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string |
| `GROQ_API_KEY` | ✅ | — | Free key from console.groq.com |
| `ADMIN_PASSWORD` | ❌ | `admin1234` | Admin panel password |
| `PORT` | ❌ | `8000` | Server port |

---

## License

MIT
