"""
Seed the database with realistic sample job descriptions.
Run:  python seed_jobs.py
Or call the API endpoint: POST /admin/seed-jobs
"""
from __future__ import annotations

SAMPLE_JOBS = [
    {
        "title": "Senior Python Backend Developer",
        "description": """We are looking for an experienced Senior Python Developer to join our engineering team.

Responsibilities:
- Design and build scalable REST APIs using FastAPI or Django REST Framework
- Manage PostgreSQL and Redis databases, write optimised queries
- Build and maintain Docker-based microservices deployed on AWS
- Participate in code reviews and mentor junior developers
- Work in an Agile/Scrum environment

Requirements:
- 5+ years of Python development experience
- Strong knowledge of FastAPI, Flask, or Django
- Proficiency in PostgreSQL, Redis, and Docker
- Experience with AWS (EC2, RDS, S3, Lambda)
- Familiarity with CI/CD pipelines (GitHub Actions, Jenkins)
- Understanding of REST API design principles and microservices

Nice to have:
- Experience with Kubernetes
- Knowledge of GraphQL
- Open-source contributions""",
        "min_experience": 5.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Data Scientist / ML Engineer",
        "description": """Join our data science team to build machine learning models that power our products.

Responsibilities:
- Develop, train, and deploy machine learning models
- Perform exploratory data analysis on large datasets
- Build NLP pipelines for text classification and sentiment analysis
- Collaborate with engineers to productionise models
- Use Python (pandas, NumPy, scikit-learn, TensorFlow/PyTorch)

Requirements:
- 3+ years of data science or ML engineering experience
- Strong Python skills with pandas, NumPy, scikit-learn
- Experience with deep learning frameworks (TensorFlow or PyTorch)
- Knowledge of NLP techniques and transformers
- Proficiency in SQL for data querying
- Experience with data visualisation tools (Matplotlib, Seaborn, Tableau)

Preferred:
- Master's or PhD in a quantitative field
- Experience with MLOps and model deployment (MLflow, SageMaker)
- Knowledge of Spark or Hadoop for big data""",
        "min_experience": 3.0,
        "education_required": "Master",
    },
    {
        "title": "Full Stack Developer (React + FastAPI)",
        "description": """We need a versatile full stack developer who can own features end-to-end.

Responsibilities:
- Build responsive React frontends with TypeScript
- Develop FastAPI or Node.js backends with PostgreSQL
- Write clean, testable code with good test coverage
- Deploy and maintain applications on cloud infrastructure
- Collaborate closely with product and design teams

Requirements:
- 3+ years full stack development experience
- Strong React and TypeScript skills
- Backend experience with Python (FastAPI/Django) or Node.js (Express)
- PostgreSQL and MongoDB database experience
- Proficiency with Docker and basic DevOps knowledge
- Experience with REST API and GraphQL
- Version control with Git/GitHub

Nice to have:
- Experience with Next.js
- Knowledge of AWS or Azure
- CI/CD experience""",
        "min_experience": 3.0,
        "education_required": "Bachelor",
    },
    {
        "title": "DevOps / Cloud Engineer",
        "description": """We are seeking a skilled DevOps Engineer to automate our infrastructure and improve deployment pipelines.

Responsibilities:
- Design and manage cloud infrastructure on AWS/Azure/GCP
- Build and maintain CI/CD pipelines using GitHub Actions and Jenkins
- Orchestrate containerised workloads with Kubernetes and Docker
- Implement infrastructure as code using Terraform and Ansible
- Monitor systems using Prometheus, Grafana, and ELK Stack
- Ensure high availability and disaster recovery

Requirements:
- 4+ years of DevOps or cloud engineering experience
- Expert-level knowledge of Docker and Kubernetes
- Hands-on experience with AWS, Azure, or GCP
- Infrastructure-as-code with Terraform or Ansible
- Experience with CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI)
- Strong Linux administration skills
- Bash and Python scripting

Certifications (bonus):
- AWS Solutions Architect or DevOps Engineer
- Kubernetes CKA/CKAD""",
        "min_experience": 4.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Frontend Developer (React / TypeScript)",
        "description": """Looking for a talented frontend developer to build exceptional user interfaces.

Responsibilities:
- Develop high-performance React applications with TypeScript
- Implement responsive UI from Figma designs using Tailwind CSS
- Optimise for performance, accessibility, and SEO
- Write unit and integration tests (Jest, React Testing Library)
- Collaborate with backend engineers on API integration

Requirements:
- 2+ years of frontend development
- Expert knowledge of React and TypeScript
- Strong HTML, CSS, and Tailwind CSS skills
- State management experience (Redux, Zustand, React Query)
- REST API and GraphQL integration experience
- Testing with Jest and React Testing Library
- Experience with Webpack or Vite build tools

Nice to have:
- Next.js experience
- Figma prototyping skills
- Performance optimisation expertise""",
        "min_experience": 2.0,
        "education_required": "Bachelor",
    },
    {
        "title": "AI / LLM Engineer",
        "description": """Join our AI team to build next-generation products powered by large language models.

Responsibilities:
- Develop and integrate LLM-based features using OpenAI, Anthropic, or open-source models
- Build and optimise RAG (Retrieval Augmented Generation) pipelines
- Design prompt engineering strategies for various use cases
- Fine-tune models using LoRA/QLoRA techniques
- Build AI agents and multi-step reasoning systems using LangChain or similar
- Evaluate and benchmark model performance

Requirements:
- 2+ years experience with LLMs and generative AI
- Strong Python skills
- Experience with OpenAI API, Anthropic Claude, or Hugging Face
- Knowledge of LangChain, LlamaIndex, or similar frameworks
- Familiarity with vector databases (Pinecone, Weaviate, Chroma)
- Prompt engineering and NLP skills
- Machine learning fundamentals

Preferred:
- Experience with fine-tuning transformer models
- Research background in NLP or machine learning
- Knowledge of deep learning frameworks (PyTorch, TensorFlow)""",
        "min_experience": 2.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Mobile Developer (React Native / Flutter)",
        "description": """We are building a cross-platform mobile app and need an experienced mobile developer.

Responsibilities:
- Develop iOS and Android apps using React Native or Flutter
- Integrate REST APIs and real-time features (WebSockets, Firebase)
- Implement native device features (camera, location, notifications)
- Optimise app performance and reduce load times
- Publish and maintain apps on App Store and Google Play

Requirements:
- 2+ years mobile development with React Native or Flutter
- Strong JavaScript/TypeScript or Dart skills
- Experience with React Native or Flutter framework
- REST API integration experience
- Knowledge of mobile UI/UX patterns
- Experience with Firebase for auth and real-time database
- App Store and Google Play publishing experience

Nice to have:
- Native iOS (Swift) or Android (Kotlin) experience
- Experience with push notifications (FCM, APNs)
- GraphQL knowledge""",
        "min_experience": 2.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Database Administrator / Data Engineer",
        "description": """We need an experienced DBA/Data Engineer to manage our data infrastructure.

Responsibilities:
- Design, optimise, and maintain PostgreSQL, MySQL, and MongoDB databases
- Build and manage ETL/ELT pipelines using Apache Airflow or dbt
- Implement data warehousing solutions
- Monitor database performance and troubleshoot bottlenecks
- Ensure data security, backup, and recovery procedures
- Work with Apache Spark and Kafka for large-scale data processing

Requirements:
- 3+ years of database administration or data engineering experience
- Expert SQL skills with PostgreSQL and MySQL
- Experience with MongoDB and Redis for NoSQL workloads
- ETL pipeline development with Airflow, dbt, or similar
- Apache Spark and Kafka knowledge for streaming pipelines
- Data warehousing experience (Redshift, BigQuery, Snowflake)
- Python scripting for automation

Nice to have:
- Cloud data platform experience (AWS Redshift, Google BigQuery)
- Tableau or Power BI for data visualisation""",
        "min_experience": 3.0,
        "education_required": "Bachelor",
    },

    # ── Non-tech jobs ──────────────────────────────────────────────────────────

    {
        "title": "Operations Manager",
        "description": """We are looking for an experienced Operations Manager to oversee daily operations.

Responsibilities:
- Supervise and manage day-to-day operational activities
- Develop and implement operational policies and procedures
- Coordinate between departments to ensure smooth workflow
- Monitor performance metrics and prepare reports
- Manage teams and conduct performance evaluations
- Handle customer complaints and resolve escalations
- Ensure compliance with company standards and regulations

Requirements:
- 5+ years of experience in operations or management
- Strong leadership and decision-making skills
- Excellent communication and problem-solving skills
- Experience in operational management and supervision
- Customer service orientation
- Proficiency in Microsoft Office (Excel, Word, PowerPoint)
- Ability to work under pressure and manage multiple priorities

Nice to have:
- Experience in government or semi-government sector
- Knowledge of quality management systems
- PMP or management certification""",
        "min_experience": 5.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Banking & Finance Professional",
        "description": """We are seeking an experienced Banking Professional to join our financial services team.

Responsibilities:
- Manage corporate and retail banking relationships
- Process loans, credit facilities, and financial products
- Handle Islamic finance products and transactions
- Conduct financial analysis and risk assessment
- Ensure compliance with banking regulations and AML policies
- Manage client portfolios and provide financial advisory
- Coordinate with internal departments for smooth transactions

Requirements:
- 5+ years of banking or financial services experience
- Knowledge of Islamic finance and banking products
- Experience in corporate banking and client relationship management
- Strong understanding of credit analysis and risk management
- Excellent communication and negotiation skills
- Proficiency in banking systems and Microsoft Office
- Knowledge of AML/KYC regulations

Preferred:
- CFA, CISI or similar financial certification
- Experience in UAE/GCC banking sector
- Arabic language proficiency""",
        "min_experience": 5.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Customer Service Representative",
        "description": """We are hiring a Customer Service Representative to deliver exceptional client experiences.

Responsibilities:
- Handle customer inquiries via phone, email, and in-person
- Resolve complaints and provide appropriate solutions
- Process customer requests and follow up to ensure resolution
- Maintain accurate records of customer interactions
- Coordinate with other departments to address customer needs
- Achieve customer satisfaction targets and KPIs
- Assist in training new team members

Requirements:
- 2+ years of customer service experience
- Excellent communication and interpersonal skills
- Strong problem-solving and conflict resolution abilities
- Ability to handle high-pressure situations professionally
- Experience with reservation systems or CRM software
- Proficiency in Microsoft Office
- Patient, empathetic, and customer-focused attitude

Nice to have:
- Experience with Amadeus or Galileo systems
- Multilingual skills (Arabic/English)
- Call center experience""",
        "min_experience": 2.0,
        "education_required": "Bachelor",
    },
    {
        "title": "HR & Administrative Officer",
        "description": """We are looking for an HR and Administrative Officer to support our human resources functions.

Responsibilities:
- Manage recruitment, onboarding, and employee records
- Coordinate training and development programs
- Handle payroll processing and attendance management
- Develop and implement HR policies and procedures
- Manage employee relations and resolve workplace issues
- Oversee administrative operations and office management
- Ensure compliance with labor laws and company policies

Requirements:
- 3+ years of HR or administrative experience
- Knowledge of HR policies, labor law, and compliance
- Experience in recruitment and performance management
- Strong organizational and communication skills
- Proficiency in Microsoft Office (Excel, Word)
- Ability to maintain confidentiality and handle sensitive information
- Attention to detail and multitasking ability

Preferred:
- CIPD, SHRM or HR certification
- Experience in UAE/GCC labor law
- Arabic language skills""",
        "min_experience": 3.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Electrical Engineer / Technician",
        "description": """We are seeking a qualified Electrical Engineer to join our technical team.

Responsibilities:
- Design, install, and maintain electrical systems and equipment
- Conduct inspections and troubleshoot electrical faults
- Ensure compliance with electrical safety standards and codes
- Coordinate with project teams for electrical installations
- Prepare technical reports and maintenance schedules
- Supervise electrical maintenance work and contractors
- Manage electrical projects from planning to completion

Requirements:
- 3+ years of electrical engineering or maintenance experience
- Strong knowledge of electrical installations and systems
- Experience in project coordination and site supervision
- Knowledge of electrical safety standards and regulations
- Ability to read and interpret electrical drawings and schematics
- Experience with maintenance and troubleshooting
- Valid electrical certification or license

Nice to have:
- Experience in industrial or construction projects
- Knowledge of PLC systems and automation
- UAE/GCC work experience""",
        "min_experience": 3.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Sales & Business Development Executive",
        "description": """We are looking for a driven Sales Executive to grow our business and client base.

Responsibilities:
- Identify and develop new business opportunities
- Build and maintain strong client relationships
- Present and pitch products/services to potential clients
- Achieve monthly and quarterly sales targets
- Prepare proposals, contracts, and sales reports
- Coordinate with operations team for client delivery
- Attend networking events and industry exhibitions

Requirements:
- 3+ years of sales or business development experience
- Proven track record of achieving sales targets
- Excellent communication and negotiation skills
- Strong customer relationship management abilities
- Experience with CRM systems
- Self-motivated and results-oriented
- Valid driving license

Preferred:
- Experience in B2B sales
- Knowledge of UAE/GCC market
- Arabic language skills""",
        "min_experience": 3.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Accountant / Finance Officer",
        "description": """We are hiring an experienced Accountant to manage our financial operations.

Responsibilities:
- Prepare financial statements and reports
- Manage accounts payable and receivable
- Conduct bank reconciliations and journal entries
- Assist in budgeting, forecasting, and financial planning
- Ensure compliance with accounting standards and tax regulations
- Process payroll and employee expense claims
- Support internal and external audits

Requirements:
- 3+ years of accounting or finance experience
- Strong knowledge of accounting principles and standards
- Proficiency in accounting software (SAP, QuickBooks, or similar)
- Advanced Excel skills for financial analysis
- Experience in financial reporting and reconciliation
- Attention to detail and analytical mindset
- Knowledge of VAT and tax regulations

Preferred:
- CPA, ACCA or CMA certification
- Experience in UAE/GCC accounting standards
- Experience with ERP systems""",
        "min_experience": 3.0,
        "education_required": "Bachelor",
    },
]


def seed(db_session=None):
    """Insert sample jobs into the database. Skip existing ones by title."""
    if db_session is None:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        from database import SessionLocal, init_db
        init_db()
        db = SessionLocal()
        close = True
    else:
        db = db_session
        close = False

    from database import JobDescription, Skill
    from matcher import extract_skills_from_text, extract_experience_from_text
    import re

    created = 0
    for job_data in SAMPLE_JOBS:
        exists = db.query(JobDescription).filter(JobDescription.title == job_data["title"]).first()
        if exists:
            continue
        job = JobDescription(
            title=job_data["title"],
            description=job_data["description"],
            min_experience=job_data.get("min_experience", 0),
            education_required=job_data.get("education_required"),
        )
        db.add(job)
        db.flush()
        for skill_name in extract_skills_from_text(job_data["description"]):
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if not skill:
                skill = Skill(name=skill_name)
                db.add(skill)
                db.flush()
            if skill not in job.required_skills:
                job.required_skills.append(skill)
        db.commit()
        created += 1
        print(f"  Created: {job.title} ({len(job.required_skills)} skills)")

    if close:
        db.close()
    return created


if __name__ == "__main__":
    print("Seeding sample jobs...")
    n = seed()
    print(f"\nDone — {n} new job(s) created.")
