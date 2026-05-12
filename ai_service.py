"""
AI integration — CV parsing + job match explanations.
Primary: Groq (free, fast LLaMA). Fallback: regex/template.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.1-8b-instant"


def _groq_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=key)
    except ImportError:
        logger.warning("groq package not installed. Run: pip install groq")
        return None
    except Exception as e:
        logger.warning("Groq init failed: %s", e)
        return None


def _generate(prompt: str, max_tokens: int = 800) -> Optional[str]:
    client = _groq_client()
    if not client:
        return None
    try:
        r = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.1,
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("Groq generation failed: %s", e)
        return None


# ── CV Parsing ─────────────────────────────────────────────────────────────────

def parse_cv_claude(text: str) -> Optional[Dict[str, Any]]:
    """Extract structured candidate data from raw CV text using AI."""
    prompt = f"""You are an expert HR analyst specializing in Gulf region (UAE/GCC) CVs. Extract structured information from this CV.

Return ONLY valid JSON with these exact keys:
- full_name: candidate's full name (string)
- email: email address (string or null)
- phone: phone number (string or null)
- linkedin: LinkedIn URL (string or null)
- github: GitHub URL (string or null)
- location: city/country (string or null)
- years_experience: total years of professional work experience as a number (0 if student/fresh graduate, count all paid jobs and internships)
- education_level: MUST be one of exactly: "PhD", "Master", "Bachelor", "Associate", "Diploma", "High School", or null
- education_field: field of study like "Business Administration", "Computer Science", "Banking", "Engineering", etc. (string or null)
- skills: array of skill strings. IMPORTANT - include ALL of:
  * Technical skills (software, tools, programming languages, certifications)
  * Professional/domain skills (banking, finance, HVAC, HR, accounting, customer service, sales, operations, media, journalism, graphic design, etc.)
  * Software tools (Microsoft Office, SAP, QuickBooks, Amadeus, Adobe Creative Suite, etc.)
  * Management skills (team leadership, project management, strategic planning, performance management, etc.)
  * Soft skills that are explicitly mentioned (communication, customer service, problem-solving, etc.)
  * Languages (arabic, english, etc.)
  * Certifications and licenses (CMA, ACCA, CPA, PMP, driving license, etc.)
  Be generous — extract 6–20 skills. Use lowercase. Do NOT skip domain/professional skills.

CV TEXT:
\"\"\"
{text[:5000]}
\"\"\"

Return ONLY the JSON object, no explanation, no markdown:"""

    raw = _generate(prompt, max_tokens=1024)
    if not raw:
        return None
    try:
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        # Extract JSON object if surrounded by other text
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            raw = m.group(0)
        data = json.loads(raw)
        data["years_experience"] = float(data.get("years_experience") or 0)
        data["skills"] = [s.lower().strip() for s in (data.get("skills") or [])]
        logger.info("Groq parsed CV: %s, %d skills", data.get("full_name"), len(data["skills"]))
        return data
    except Exception as e:
        logger.warning("Groq CV parse JSON error: %s | raw: %s", e, raw[:200])
        return None


# ── Job Match Explanation ──────────────────────────────────────────────────────

def explain_match(
    candidate_name: str,
    candidate_skills: List[str],
    candidate_exp: float,
    candidate_edu: Optional[str],
    job_title: str,
    required_skills: List[str],
    min_exp: float,
    edu_required: Optional[str],
    matched: List[str],
    missing: List[str],
    score: float,
) -> str:
    prompt = f"""Write exactly 2 short sentences (max 50 words total) explaining why this job is a {score:.0f}% match.
Be specific and mention actual skills. No bullet points. No greetings.

Candidate: {candidate_name} | {candidate_exp} yrs | {candidate_edu or 'unspecified'}
Job: {job_title} | {min_exp}+ yrs required
Matched skills: {', '.join(matched[:5]) or 'none'}
Missing skills: {', '.join(missing[:3]) or 'none'}

2 sentences only:"""

    result = _generate(prompt, max_tokens=100)
    if result:
        return result
    return _fallback_explanation(candidate_exp, min_exp, matched, missing, score)


def _fallback_explanation(
    candidate_exp: float, min_exp: float,
    matched: List[str], missing: List[str], score: float,
) -> str:
    parts = []
    if matched:
        parts.append(f"Your skills in {', '.join(matched[:3])} align well with this role")
    if candidate_exp >= (min_exp or 0):
        parts.append("your experience meets the requirement")
    elif min_exp > 0:
        parts.append(f"consider building more experience to meet the {min_exp}-year requirement")
    if missing:
        parts.append(f"adding {', '.join(missing[:2])} would strengthen your application")
    if not parts:
        return f"This role is a {score:.0f}% match based on your overall profile."
    return ". ".join(parts).capitalize() + "."


# ── Career Coach ──────────────────────────────────────────────────────────────

# Real course links by field and skill gap
COURSE_LINKS: Dict[str, Dict[str, Any]] = {
    # ── Finance / Accounting ────────────────────────────────────────────────────
    "cma":              {"title": "CMA Certification", "url": "https://www.imanet.org/cma-certification", "platform": "IMA", "free": False},
    "cpa":              {"title": "CPA Exam Prep", "url": "https://www.aicpa-cima.com/certifications/certified-public-accountant", "platform": "AICPA", "free": False},
    "acca":             {"title": "ACCA Qualification", "url": "https://www.accaglobal.com/gb/en/qualifications/glance/acca.html", "platform": "ACCA", "free": False},
    "cfa":              {"title": "CFA Program", "url": "https://www.cfainstitute.org/programs/cfa", "platform": "CFA Institute", "free": False},
    "ifrs":             {"title": "IFRS Certificate", "url": "https://www.coursera.org/learn/uol-financial-reporting", "platform": "Coursera", "free": True},
    "financial modeling": {"title": "Financial Modeling", "url": "https://www.coursera.org/learn/wharton-financial-accounting", "platform": "Coursera (Wharton)", "free": True},
    "excel":            {"title": "Excel for Finance", "url": "https://www.coursera.org/learn/excel-vba-for-creative-problem-solving", "platform": "Coursera", "free": True},
    "sap":              {"title": "SAP Free Learning", "url": "https://learning.sap.com/courses", "platform": "SAP Learning Hub", "free": True},
    "quickbooks":       {"title": "QuickBooks Training", "url": "https://quickbooks.intuit.com/learn-support/en-us/", "platform": "Intuit", "free": True},
    "vat":              {"title": "UAE VAT Course", "url": "https://www.udemy.com/course/uae-vat-complete-guide/", "platform": "Udemy", "free": False},
    "tax":              {"title": "UAE Corporate Tax", "url": "https://www.tax.gov.ae/en/services/elearning.aspx", "platform": "UAE FTA", "free": True},
    # ── HR ──────────────────────────────────────────────────────────────────────
    "cipd":             {"title": "CIPD HR Qualification", "url": "https://www.cipd.org/en/qualifications/", "platform": "CIPD", "free": False},
    "shrm":             {"title": "SHRM Certification", "url": "https://www.shrm.org/credentials/certifications", "platform": "SHRM", "free": False},
    "hr analytics":     {"title": "HR Analytics", "url": "https://www.coursera.org/learn/people-analytics", "platform": "Coursera (Wharton)", "free": True},
    "recruitment":      {"title": "Talent Acquisition", "url": "https://www.linkedin.com/learning/topics/recruiting", "platform": "LinkedIn Learning", "free": False},
    "payroll":          {"title": "Payroll Management", "url": "https://www.udemy.com/topic/payroll/", "platform": "Udemy", "free": False},
    # ── Operations / Management ─────────────────────────────────────────────────
    "pmp":              {"title": "PMP Certification", "url": "https://www.pmi.org/certifications/project-management-pmp", "platform": "PMI", "free": False},
    "six sigma":        {"title": "Six Sigma Green Belt", "url": "https://www.coursera.org/learn/six-sigma-fundamentals", "platform": "Coursera", "free": True},
    "lean":             {"title": "Lean Management", "url": "https://www.edx.org/learn/lean-management", "platform": "edX", "free": True},
    "iso":              {"title": "ISO 9001 Quality", "url": "https://www.udemy.com/topic/iso-9001/", "platform": "Udemy", "free": False},
    "strategic planning": {"title": "Strategic Planning", "url": "https://www.coursera.org/learn/strategy-business", "platform": "Coursera", "free": True},
    # ── Sales / Marketing ───────────────────────────────────────────────────────
    "digital marketing": {"title": "Google Digital Marketing", "url": "https://skillshop.withgoogle.com/", "platform": "Google Skillshop", "free": True},
    "social media":     {"title": "Social Media Marketing", "url": "https://www.coursera.org/learn/social-media-marketing", "platform": "Coursera", "free": True},
    "seo":              {"title": "SEO Fundamentals", "url": "https://www.semrush.com/academy/courses/", "platform": "SEMrush Academy", "free": True},
    "crm":              {"title": "CRM & Salesforce", "url": "https://trailhead.salesforce.com/en/home", "platform": "Salesforce Trailhead", "free": True},
    # ── IT / Tech ───────────────────────────────────────────────────────────────
    "python":           {"title": "Python for Everybody", "url": "https://www.coursera.org/specializations/python", "platform": "Coursera (Michigan)", "free": True},
    "sql":              {"title": "SQL for Beginners", "url": "https://www.w3schools.com/sql/", "platform": "W3Schools", "free": True},
    "data analysis":    {"title": "Google Data Analytics", "url": "https://www.coursera.org/professional-certificates/google-data-analytics", "platform": "Coursera", "free": True},
    "power bi":         {"title": "Power BI Tutorial", "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi", "platform": "Microsoft Learn", "free": True},
    "cybersecurity":    {"title": "Google Cybersecurity", "url": "https://www.coursera.org/professional-certificates/google-cybersecurity", "platform": "Coursera", "free": True},
    "cloud":            {"title": "AWS Cloud Practitioner", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "platform": "AWS Training", "free": True},
    # ── Engineering ─────────────────────────────────────────────────────────────
    "autocad":          {"title": "AutoCAD Essentials", "url": "https://www.autodesk.com/certification/learn/catalog", "platform": "Autodesk", "free": True},
    "plc":              {"title": "PLC Programming", "url": "https://www.udemy.com/topic/plc-programming/", "platform": "Udemy", "free": False},
    "hvac":             {"title": "HVAC Fundamentals", "url": "https://www.udemy.com/topic/hvac/", "platform": "Udemy", "free": False},
    "electrical engineering": {"title": "Electrical Engineering", "url": "https://www.edx.org/learn/electrical-engineering", "platform": "edX", "free": True},
    "project management": {"title": "Engineering Project Mgmt", "url": "https://www.coursera.org/specializations/engineering-project-management", "platform": "Coursera (Rice)", "free": True},
    # ── Medical / Healthcare ─────────────────────────────────────────────────────
    "patient care":     {"title": "Patient Safety", "url": "https://www.coursera.org/learn/patient-safety", "platform": "Coursera", "free": True},
    "healthcare management": {"title": "Healthcare Management", "url": "https://www.coursera.org/learn/healthcare-organizations", "platform": "Coursera", "free": True},
    "pharmacy":         {"title": "Clinical Pharmacy", "url": "https://www.coursera.org/learn/pharmacy", "platform": "Coursera", "free": True},
    "nursing":          {"title": "Nursing & Patient Care", "url": "https://www.edx.org/learn/nursing", "platform": "edX", "free": True},
    "medical coding":   {"title": "Medical Coding", "url": "https://www.coursera.org/learn/medical-billing-coding", "platform": "Coursera", "free": True},
    # ── Languages / Soft Skills ──────────────────────────────────────────────────
    "english":          {"title": "Business English", "url": "https://www.coursera.org/learn/business-english-networking", "platform": "Coursera", "free": True},
    "communication":    {"title": "Professional Communication", "url": "https://www.coursera.org/learn/communication-skills", "platform": "Coursera", "free": True},
    "leadership":       {"title": "Leadership Skills", "url": "https://www.coursera.org/learn/leadership-skills-management", "platform": "Coursera", "free": True},
    # ── UAE-specific ─────────────────────────────────────────────────────────────
    "uae labor law":    {"title": "UAE Labor Law", "url": "https://www.udemy.com/course/uae-labor-law/", "platform": "Udemy", "free": False},
    "aml kyc":          {"title": "AML/KYC Compliance", "url": "https://www.udemy.com/topic/anti-money-laundering/", "platform": "Udemy", "free": False},
    "islamic finance":  {"title": "Islamic Finance", "url": "https://www.coursera.org/learn/islamic-finance", "platform": "Coursera", "free": True},
}


def career_coach_analysis(
    name: str,
    skills: List[str],
    exp: float,
    edu: Optional[str],
    edu_field: Optional[str],
    raw_text: str,
) -> Optional[Dict[str, Any]]:
    """
    Generate a full career coaching report:
    strengths, skill gaps, action plan with real course links, career roadmap.
    Covers: office/admin, engineering, medical fields — UAE market focused.
    """

    skills_str = ", ".join(skills[:30]) if skills else "not specified"

    prompt = f"""You are an expert UAE career coach. Analyze this professional profile and return a detailed career development report.

Candidate: {name}
Experience: {exp} years
Education: {edu or 'not specified'} in {edu_field or 'not specified'}
Skills: {skills_str}

Return ONLY valid JSON with this exact structure:
{{
  "field": "one of: Finance & Accounting | Human Resources | Operations & Management | Sales & Marketing | Information Technology | Electrical Engineering | Mechanical Engineering | Civil Engineering | HVAC & Facilities | Healthcare & Nursing | Pharmacy & Medical | Administrative & Office | Media & Communications | Customer Service | Other",
  "current_level": "one of: Entry Level | Junior | Mid-Level | Senior | Manager | Director",
  "next_level": "one of: Junior | Mid-Level | Senior | Manager | Director | Executive",
  "strengths": ["3-5 specific strength points based on their actual skills and experience"],
  "gaps": [
    {{
      "skill": "specific missing skill or certification name",
      "importance": "one of: Critical | High | Medium",
      "why": "one sentence why this matters in UAE job market"
    }}
  ],
  "action_plan": [
    {{
      "step": 1,
      "action": "specific action to take",
      "duration": "e.g. 1 month, 3 months, 6 months",
      "skill_gained": "exact skill name matching COURSE_LINKS keys if possible"
    }}
  ],
  "career_path": [
    {{"level": "current title", "timeline": "Now", "key_skills": ["skill1", "skill2"]}},
    {{"level": "next title", "timeline": "1-2 years", "key_skills": ["skill1", "skill2"]}},
    {{"level": "future title", "timeline": "3-5 years", "key_skills": ["skill1", "skill2"]}}
  ],
  "uae_tip": "one specific career tip relevant to UAE/GCC job market"
}}

Rules:
- gaps: list 3-5 most important missing skills for their field and level
- action_plan: 3-5 concrete steps, ordered by priority
- skill_gained in action_plan should match common skills like: cma, pmp, ifrs, excel, python, sql, digital marketing, seo, autocad, hvac, plc, patient care, english, leadership, etc.
- Be specific to UAE job market
- Return ONLY the JSON, no explanation:"""

    raw = _generate(prompt, max_tokens=1500)
    if not raw:
        return _fallback_career_coach(name, skills, exp, edu)

    try:
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            raw = m.group(0)
        data = json.loads(raw)

        # Attach real course links to each gap and action step
        for gap in data.get("gaps", []):
            skill_key = gap.get("skill", "").lower()
            link = _find_course_link(skill_key)
            gap["course"] = link

        for step in data.get("action_plan", []):
            skill_key = step.get("skill_gained", "").lower()
            link = _find_course_link(skill_key)
            step["course"] = link

        logger.info("Career coach report generated for: %s | field: %s", name, data.get("field"))
        return data

    except Exception as e:
        logger.warning("Career coach JSON error: %s | raw: %s", e, raw[:300])
        return _fallback_career_coach(name, skills, exp, edu)


def _find_course_link(skill_key: str) -> Optional[Dict]:
    """Find the best matching course link for a skill."""
    if not skill_key:
        return None
    # Exact match first
    if skill_key in COURSE_LINKS:
        return COURSE_LINKS[skill_key]
    # Partial match
    for key, val in COURSE_LINKS.items():
        if key in skill_key or skill_key in key:
            return val
    return None


def _fallback_career_coach(
    name: str, skills: List[str], exp: float, edu: Optional[str]
) -> Dict[str, Any]:
    """Fallback report when AI is unavailable."""
    return {
        "field": "General Professional",
        "current_level": "Mid-Level" if exp >= 5 else "Junior" if exp >= 2 else "Entry Level",
        "next_level": "Senior" if exp >= 5 else "Mid-Level" if exp >= 2 else "Junior",
        "strengths": [
            f"You have {exp:.0f} years of professional experience",
            f"Your profile includes {len(skills)} identified skills",
            f"Education level: {edu or 'specified on CV'}",
        ],
        "gaps": [
            {"skill": "Professional Certification", "importance": "High",
             "why": "Certifications significantly boost salary and job prospects in UAE",
             "course": COURSE_LINKS.get("leadership")},
            {"skill": "Digital Skills", "importance": "High",
             "why": "Digital literacy is essential in UAE's modern workplace",
             "course": COURSE_LINKS.get("digital marketing")},
        ],
        "action_plan": [
            {"step": 1, "action": "Identify and obtain a relevant professional certification",
             "duration": "3-6 months", "skill_gained": "certification",
             "course": COURSE_LINKS.get("leadership")},
            {"step": 2, "action": "Strengthen digital skills relevant to your field",
             "duration": "1-2 months", "skill_gained": "digital skills",
             "course": COURSE_LINKS.get("digital marketing")},
        ],
        "career_path": [
            {"level": "Current Role", "timeline": "Now", "key_skills": skills[:3]},
            {"level": "Senior Role", "timeline": "1-2 years", "key_skills": ["certification", "leadership"]},
            {"level": "Management", "timeline": "3-5 years", "key_skills": ["strategic planning", "team management"]},
        ],
        "uae_tip": "In the UAE job market, professional certifications and bilingual (Arabic/English) communication skills significantly increase your competitiveness.",
    }


# ── CV Score ───────────────────────────────────────────────────────────────────

def cv_score_analysis(
    name: str,
    skills: List[str],
    exp: float,
    edu: Optional[str],
    edu_field: Optional[str],
    raw_text: str,
) -> Dict[str, Any]:
    """Score a CV out of 100 and return section breakdown + improvement tips."""

    prompt = f"""You are a senior HR recruiter in the UAE. Evaluate this CV and return a detailed quality score.

Candidate: {name}
Experience: {exp} years
Education: {edu or 'not specified'} in {edu_field or 'not specified'}
Skills: {', '.join(skills[:30]) if skills else 'none detected'}
CV Text (first 800 chars): {raw_text[:800]}

Return ONLY valid JSON:
{{
  "total_score": <integer 0-100>,
  "grade": <"A" | "B" | "C" | "D">,
  "summary": "<one sentence overall verdict>",
  "sections": [
    {{"name": "Contact & Profile", "score": <0-10>, "max": 10, "feedback": "<specific feedback>"}},
    {{"name": "Work Experience", "score": <0-25>, "max": 25, "feedback": "<specific feedback>"}},
    {{"name": "Skills", "score": <0-25>, "max": 25, "feedback": "<specific feedback>"}},
    {{"name": "Education", "score": <0-20>, "max": 20, "feedback": "<specific feedback>"}},
    {{"name": "CV Structure & Clarity", "score": <0-20>, "max": 20, "feedback": "<specific feedback>"}}
  ],
  "quick_wins": [
    "<actionable tip 1 — specific change to make right now>",
    "<actionable tip 2>",
    "<actionable tip 3>"
  ],
  "ats_tip": "<one tip about ATS/keyword optimization for UAE job boards>"
}}

Be honest and specific. Base feedback on the actual CV content provided."""

    raw = _generate(prompt, max_tokens=900)
    if not raw:
        return _fallback_cv_score(skills, exp, edu)
    try:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return _fallback_cv_score(skills, exp, edu)
        data = json.loads(m.group())
        return data
    except Exception as e:
        logger.warning("CV score JSON error: %s", e)
        return _fallback_cv_score(skills, exp, edu)


def _fallback_cv_score(skills: List[str], exp: float, edu: Optional[str]) -> Dict[str, Any]:
    skill_score = min(25, len(skills) * 2)
    exp_score = min(25, int(exp * 3))
    edu_score = 15 if edu and any(x in (edu or '').lower() for x in ['bachelor', 'master', 'phd']) else 10
    total = 10 + exp_score + skill_score + edu_score + 12
    grade = 'A' if total >= 80 else 'B' if total >= 65 else 'C' if total >= 50 else 'D'
    return {
        "total_score": total,
        "grade": grade,
        "summary": f"CV shows {len(skills)} skills and {exp:.0f} years of experience.",
        "sections": [
            {"name": "Contact & Profile", "score": 8, "max": 10, "feedback": "Ensure email and phone are clearly visible."},
            {"name": "Work Experience", "score": exp_score, "max": 25, "feedback": "Add quantified achievements to each role."},
            {"name": "Skills", "score": skill_score, "max": 25, "feedback": "List technical and soft skills clearly."},
            {"name": "Education", "score": edu_score, "max": 20, "feedback": "Include graduation year and GPA if strong."},
            {"name": "CV Structure & Clarity", "score": 12, "max": 20, "feedback": "Use clear headings and consistent formatting."},
        ],
        "quick_wins": [
            "Add a 2–3 line professional summary at the top",
            "Quantify achievements: use numbers and percentages",
            "Add relevant keywords from job descriptions",
        ],
        "ats_tip": "Use standard section headings (Experience, Education, Skills) so ATS systems can parse your CV correctly.",
    }


# ── Interview Prep ─────────────────────────────────────────────────────────────

def interview_prep(
    job_title: str,
    job_description: str,
    required_skills: List[str],
    candidate_skills: List[str],
    exp: float,
) -> Dict[str, Any]:
    """Generate tailored interview Q&A for a specific job."""

    missing = [s for s in required_skills if s not in candidate_skills][:5]

    prompt = f"""You are an expert interview coach. Generate realistic interview questions for this job application.

Job Title: {job_title}
Key Required Skills: {', '.join(required_skills[:10])}
Candidate Experience: {exp} years
Candidate's Missing Skills: {', '.join(missing) if missing else 'none'}

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "<interview question>",
      "type": "<Technical | Behavioral | Situational>",
      "why_asked": "<one sentence — why interviewers ask this>",
      "answer_tip": "<how to structure a strong answer, 1-2 sentences>"
    }}
  ],
  "general_tips": [
    "<interview tip 1 specific to this role>",
    "<interview tip 2>",
    "<interview tip 3>"
  ],
  "dress_code": "<appropriate dress code for this role in UAE>",
  "salary_negotiation": "<one tip for salary negotiation for this role in UAE>"
}}

Generate 8 questions: 3 technical, 3 behavioral, 2 situational. Make them realistic and role-specific."""

    raw = _generate(prompt, max_tokens=1200)
    if not raw:
        return _fallback_interview_prep(job_title, required_skills)
    try:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return _fallback_interview_prep(job_title, required_skills)
        data = json.loads(m.group())
        return data
    except Exception as e:
        logger.warning("Interview prep JSON error: %s", e)
        return _fallback_interview_prep(job_title, required_skills)


def _fallback_interview_prep(job_title: str, required_skills: List[str]) -> Dict[str, Any]:
    skills_str = ', '.join(required_skills[:3]) if required_skills else 'relevant skills'
    return {
        "questions": [
            {"question": f"Tell me about your experience with {skills_str}.", "type": "Technical",
             "why_asked": "To assess technical depth.", "answer_tip": "Give a specific example with measurable results."},
            {"question": "Walk me through a challenging project you led.", "type": "Behavioral",
             "why_asked": "To assess problem-solving and leadership.", "answer_tip": "Use the STAR method: Situation, Task, Action, Result."},
            {"question": f"Why are you interested in the {job_title} role?", "type": "Behavioral",
             "why_asked": "To assess motivation and cultural fit.", "answer_tip": "Connect your background to the role's requirements."},
            {"question": "How do you handle tight deadlines and multiple priorities?", "type": "Situational",
             "why_asked": "To assess time management.", "answer_tip": "Describe your prioritization system with a real example."},
            {"question": "What are your salary expectations?", "type": "Situational",
             "why_asked": "To assess fit within budget.", "answer_tip": "Research market rates and give a range based on your experience."},
        ],
        "general_tips": [
            "Research the company thoroughly before the interview",
            "Prepare 2–3 questions to ask the interviewer",
            "Bring multiple printed copies of your CV",
        ],
        "dress_code": "Business professional or smart casual depending on the company culture.",
        "salary_negotiation": "Research market rates on LinkedIn Salary and Bayt.com before negotiating.",
    }


# ── Salary Estimator ───────────────────────────────────────────────────────────

def salary_estimate(
    skills: List[str],
    exp: float,
    edu: Optional[str],
    edu_field: Optional[str],
    location: str = "UAE",
) -> Dict[str, Any]:
    """Estimate monthly salary range in AED for the UAE/Gulf market."""

    prompt = f"""You are a UAE compensation specialist. Use these REAL 2024-2025 UAE monthly salary benchmarks (AED) to guide your answer:

SALARY BENCHMARKS (monthly AED, gross):
- Software Engineer: Junior 8k-12k | Mid 14k-22k | Senior 25k-40k
- Data Analyst / BI: Junior 7k-11k | Mid 13k-20k | Senior 22k-35k
- DevOps / Cloud: Mid 18k-28k | Senior 30k-45k
- Accountant: Junior 5k-8k | Mid 9k-15k | Senior 16k-25k
- Finance Manager / CFO: Senior 25k-45k | Director 50k-90k
- CMA / CPA holder: +20-30% premium over base
- HR Specialist: Junior 6k-9k | Mid 10k-16k | Senior 18k-28k
- HR Manager: 22k-40k
- Marketing / Digital Marketing: Junior 6k-10k | Mid 11k-18k | Senior 20k-32k
- Sales Executive: Base 6k-12k + commission (OTE 15k-35k)
- Operations Manager: Mid 15k-25k | Senior 28k-45k
- Administrative Assistant: 4k-8k
- Office Manager: 8k-15k
- Civil/Mechanical/Electrical Engineer: Junior 8k-14k | Mid 15k-25k | Senior 28k-45k
- HVAC Technician: 5k-12k
- Nurse (RN): 8k-16k (+ housing allowance)
- Doctor/Physician: 25k-70k depending on specialty
- Pharmacist: 10k-20k
- Teacher / School Principal: Teacher 8k-16k | Principal 20k-40k
- Customer Service Rep: 4k-7k
- Call Center Team Leader: 8k-14k
- Graphic Designer: 6k-12k
- PR / Communications: 10k-22k
- IT Support: 6k-12k
- Project Manager (PMP): 20k-40k

Candidate Profile:
- Experience: {exp} years
- Education: {edu or 'not specified'} in {edu_field or 'not specified'}
- Skills: {', '.join(skills[:25]) if skills else 'not specified'}

Instructions:
1. Identify the most likely role from the skills/edu
2. Pick the appropriate experience band (junior <3 yrs, mid 3-7, senior 7+, manager 10+)
3. Use the benchmarks above — do NOT invent numbers outside these realistic ranges
4. min should be ~15% below mid, max ~25% above mid

Return ONLY valid JSON:
{{
  "role_detected": "<specific job title>",
  "field": "<industry>",
  "salary_aed": {{
    "min": <integer>,
    "mid": <integer>,
    "max": <integer>
  }},
  "level": "<Junior | Mid-Level | Senior | Manager>",
  "factors": [
    {{"factor": "<factor>", "impact": "<Positive | Negative | Neutral>", "detail": "<one sentence>"}}
  ],
  "negotiation_range": "<e.g. AED 14,000 – 18,000>",
  "top_paying_companies": ["<UAE company 1>", "<UAE company 2>", "<UAE company 3>"],
  "market_note": "<one realistic sentence about this profile in UAE 2025>"
}}"""

    raw = _generate(prompt, max_tokens=800)
    if not raw:
        return _fallback_salary(skills, exp, edu)
    try:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return _fallback_salary(skills, exp, edu)
        data = json.loads(m.group())
        return data
    except Exception as e:
        logger.warning("Salary estimate JSON error: %s", e)
        return _fallback_salary(skills, exp, edu)


def _fallback_salary(skills: List[str], exp: float, edu: Optional[str]) -> Dict[str, Any]:
    # Realistic UAE salary bands by experience
    if exp < 2:
        mid = 7000
    elif exp < 5:
        mid = 12000
    elif exp < 9:
        mid = 20000
    else:
        mid = 30000
    # Education bonus
    if edu and 'master' in (edu or '').lower():
        mid = int(mid * 1.2)
    elif edu and ('bachelor' in (edu or '').lower() or 'bsc' in (edu or '').lower()):
        mid = int(mid * 1.1)
    level = "Senior" if exp >= 8 else "Mid-Level" if exp >= 3 else "Junior"
    return {
        "role_detected": "Professional",
        "field": "General",
        "salary_aed": {"min": int(mid * 0.85), "mid": mid, "max": int(mid * 1.25)},
        "level": level,
        "factors": [
            {"factor": "Years of Experience", "impact": "Positive", "detail": f"{exp:.0f} years of experience is a strong asset."},
            {"factor": "UAE Market Demand", "impact": "Positive", "detail": "UAE has high demand for experienced professionals."},
        ],
        "negotiation_range": f"AED {int(mid*0.9):,} – {int(mid*1.2):,}",
        "top_paying_companies": ["ADNOC", "Emirates Group", "Dubai Holding"],
        "market_note": "UAE salaries are tax-free, making them highly competitive globally.",
    }


# ── Profile Summary ────────────────────────────────────────────────────────────

def summarise_profile(
    name: str, skills: List[str], exp: float,
    edu: Optional[str], matched_jobs_count: int,
) -> str:
    prompt = f"""Write 2 short encouraging sentences for a job seeker profile. No greetings, no bullet points.
Name: {name} | Experience: {exp} yrs | Education: {edu or 'not specified'}
Top skills: {', '.join(skills[:10])}
Matching jobs found: {matched_jobs_count}
2 sentences:"""

    result = _generate(prompt, max_tokens=120)
    if result:
        return result
    return (
        f"We detected {len(skills)} skills in your CV including "
        f"{', '.join(skills[:4])}{'...' if len(skills) > 4 else ''}. "
        f"Found {matched_jobs_count} matching job{'s' if matched_jobs_count != 1 else ''} for you."
    )
