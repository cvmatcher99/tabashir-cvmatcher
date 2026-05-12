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

    # ── Non-tech jobs (existing) ───────────────────────────────────────────────

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

    # ── Additional Gulf-region jobs ─────────────────────────────────────────────

    {
        "title": "Media & Content Production Specialist",
        "description": """We are looking for a creative Media and Content Production Specialist to join our communications team.

Responsibilities:
- Produce and coordinate digital content for broadcast, web, and social media platforms
- Write and edit scripts for video, audio, and multimedia productions
- Present on-camera and record professional voiceovers for various content formats
- Manage social media accounts and create engaging digital storytelling content
- Produce and host podcasts and audio/video features
- Collaborate with editorial and creative teams on news and feature stories
- Manage story development from concept to final delivery

Requirements:
- 2+ years of experience in media, journalism, or content production
- Proven skills in scripting, video production, and content creation
- Experience in social media management and digital storytelling
- On-camera presenting and voiceover skills
- Strong communication and writing skills in English and/or Arabic
- Proficiency in video editing software and multimedia tools
- Ability to work in a fast-paced newsroom or media environment

Nice to have:
- Experience in broadcast journalism (TV, radio, online)
- Podcast production experience
- Bilingual (Arabic/English)
- Portfolio of published multimedia content""",
        "min_experience": 2.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Graphic Designer / Visual Content Creator",
        "description": """We are seeking a talented Graphic Designer to produce high-quality visual content for our brand.

Responsibilities:
- Design graphics, banners, and marketing materials for digital and print
- Create and schedule social media posts and visual content
- Edit photos and produce short-form video content
- Design presentations, brochures, and corporate communications
- Maintain brand consistency across all visual assets
- Collaborate with marketing and communications teams

Requirements:
- Experience in graphic design, photo editing, and visual content creation
- Proficiency in Adobe Creative Suite (Photoshop, Illustrator, InDesign) or Canva
- Photo and video editing skills
- Experience with social media content creation
- Strong eye for design, color, and typography
- Microsoft Office proficiency (PowerPoint, Word)
- Attention to detail and ability to meet deadlines

Nice to have:
- Experience with motion graphics or animation
- Social media management experience
- Arabic language skills
- Portfolio of design work""",
        "min_experience": 1.0,
        "education_required": "High School",
    },
    {
        "title": "HVAC Technician / Facilities Maintenance",
        "description": """We are hiring a skilled HVAC Technician to maintain and repair air conditioning and refrigeration systems.

Responsibilities:
- Install, maintain, and repair air conditioning, split AC, and refrigeration systems
- Diagnose and troubleshoot mechanical and electrical faults in HVAC equipment
- Perform scheduled preventive maintenance on cooling and ventilation systems
- Ensure compliance with quality, safety, and health standards
- Maintain service records and prepare maintenance reports
- Respond to emergency breakdowns and urgent maintenance calls
- Coordinate with facilities management and building operations teams

Requirements:
- 3+ years of HVAC maintenance and installation experience
- Hands-on experience with split AC systems, chillers, and refrigeration
- Ability to diagnose mechanical and electrical faults
- Knowledge of safety standards and compliance regulations
- Technical diploma or certification in refrigeration and air conditioning
- Teamwork and communication skills

Nice to have:
- Experience in facilities management companies
- Knowledge of BMS (Building Management Systems)
- UAE/GCC work experience
- Valid UAE driving license""",
        "min_experience": 3.0,
        "education_required": "Associate",
    },
    {
        "title": "Senior Finance Manager / CFO",
        "description": """We are seeking an experienced Senior Finance Manager to lead our financial operations and strategy.

Responsibilities:
- Lead financial planning, budgeting, forecasting, and strategic cost optimization
- Ensure full IFRS compliance and prepare consolidated financial statements
- Manage UAE corporate tax filings, VAT returns, and regulatory reporting
- Oversee ERP systems implementation and financial process automation
- Drive business growth through financial analysis and management reporting
- Manage and mentor the finance team
- Liaise with auditors, banks, and regulatory authorities

Requirements:
- 10+ years of financial management experience in UAE/GCC
- CMA, CPA, ACCA, or equivalent professional certification
- Deep knowledge of IFRS, UAE corporate tax, and VAT regulations
- Proven experience with ERP systems (SAP, Oracle, or similar)
- Strong skills in budgeting, forecasting, and financial modelling
- Experience managing finance teams and presenting to senior leadership
- Bachelor's degree in Accounting, Finance, or Commerce

Preferred:
- Certified UAE Tax Agent or IFRS certification
- Experience in multi-entity corporate group finance
- Arabic language proficiency""",
        "min_experience": 10.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Strategic Planning & Government Affairs Manager",
        "description": """We are looking for a seasoned Strategic Planning professional to drive organizational excellence.

Responsibilities:
- Develop and implement organizational strategic plans aligned with national vision
- Design and manage KPIs, performance management frameworks, and balanced scorecards
- Lead institutional excellence initiatives and quality management programs
- Coordinate cross-functional teams and manage government relations
- Prepare executive reports and strategic presentations for senior leadership
- Drive continuous improvement and change management initiatives
- Represent the organization in government and semi-government forums

Requirements:
- 10+ years of experience in strategic planning or government management
- Proven expertise in KPI development and performance management
- Experience in institutional excellence frameworks (EFQM, ISO, etc.)
- Strong leadership and cross-functional team management
- Excellent Arabic and English communication skills
- Bachelor's degree in Business Administration, Public Administration, or related field

Preferred:
- Experience in UAE government or semi-government sector
- PMP, Lean Six Sigma, or equivalent certification
- Master's degree in Strategic Management or Public Policy
- Knowledge of UAE National Vision and federal strategies""",
        "min_experience": 10.0,
        "education_required": "Bachelor",
    },
    {
        "title": "School Principal / Education Manager",
        "description": """We are seeking an experienced education leader to serve as School Principal and drive academic excellence.

Responsibilities:
- Lead school operations, academic programs, and institutional development
- Drive accreditation processes and quality assurance standards
- Develop strategic plans to improve student outcomes and enrollment
- Manage teaching staff, conduct performance evaluations, and provide mentoring
- Foster a culture of leadership, innovation, and continuous improvement
- Handle crisis management, parent relations, and community engagement
- Prepare reports for regulatory bodies and education authorities

Requirements:
- 10+ years of experience in education management or school leadership
- Proven track record in school administration and academic leadership
- Experience with accreditation bodies (Cognia, KHDA, or equivalent)
- Strong skills in strategic planning, quality assurance, and staff development
- Excellent leadership, communication, and problem-solving skills
- Bachelor's or Master's degree in Education or Education Management

Preferred:
- Experience in UAE/GCC education sector
- Knowledge of international accreditation standards
- Arabic language proficiency
- Awards or recognition for educational excellence""",
        "min_experience": 10.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Administrative Assistant / Office Coordinator",
        "description": """We are looking for a reliable and organized Administrative Assistant to support our office operations.

Responsibilities:
- Provide administrative and clerical support to management and office staff
- Manage correspondence, filing, scheduling, and document management
- Handle data entry, report preparation, and spreadsheet management
- Coordinate meetings, events, and office logistics
- Assist with reception duties and visitor management
- Support HR and operations functions as needed
- Manage office supplies and coordinate with vendors

Requirements:
- Strong organizational and time management skills
- Proficiency in Microsoft Office (Word, Excel, PowerPoint, Outlook)
- Excellent communication and interpersonal skills
- Data entry and document management experience
- Ability to multitask and work in a team environment
- Attention to detail and professional attitude
- Arabic and English language skills

Nice to have:
- Experience in UAE government or corporate environment
- Graphic design or presentation skills
- Experience with Adobe Creative Suite or Canva
- Valid UAE driving license""",
        "min_experience": 0.0,
        "education_required": "High School",
    },
    {
        "title": "Social Media Manager / Digital Marketing Executive",
        "description": """We are hiring a Social Media Manager to grow our digital presence and engage our audience.

Responsibilities:
- Create, schedule, and publish engaging content across social media platforms
- Develop and implement social media strategies aligned with marketing goals
- Produce graphic designs, photos, and short videos for digital campaigns
- Monitor analytics and report on social media performance and KPIs
- Manage online community engagement and respond to comments/messages
- Collaborate with content, marketing, and creative teams
- Stay up to date with social media trends and platform updates

Requirements:
- Experience in social media management and digital content creation
- Proficiency in content creation tools (Canva, Adobe Creative Suite, or similar)
- Photo and video editing skills for social media formats
- Strong written and visual communication skills
- Understanding of social media analytics and reporting
- Creativity and ability to develop engaging digital campaigns
- Arabic and/or English language skills

Nice to have:
- Experience with paid social media advertising (Meta Ads, TikTok Ads)
- Graphic design background
- Experience in UAE/GCC markets
- Google Analytics or Meta Business Suite certification""",
        "min_experience": 1.0,
        "education_required": "High School",
    },
    {
        "title": "Public Relations & Communications Officer",
        "description": """We are seeking a skilled PR and Communications Officer to manage our public image and media relations.

Responsibilities:
- Develop and implement public relations and communications strategies
- Manage media relations, press releases, and corporate communications
- Handle customer service escalations and client relationship management
- Coordinate with banking, financial, or corporate clients
- Manage call center operations and ensure quality service delivery
- Prepare communications reports, briefings, and executive presentations
- Represent the organization at external events and forums

Requirements:
- 3+ years of experience in public relations, communications, or customer service
- Excellent verbal and written communication skills in Arabic and English
- Experience in media relations, corporate communications, or banking PR
- Strong customer relationship management abilities
- Proficiency in Microsoft Office and social media platforms
- Ability to handle high-pressure situations and manage multiple stakeholders
- Bachelor's degree in Public Relations, Media, Communications, or related field

Preferred:
- Experience in UAE banking or financial services sector
- Knowledge of compliance and regulatory communication requirements
- Experience with CRM systems
- Arabic media writing skills""",
        "min_experience": 3.0,
        "education_required": "Bachelor",
    },
    {
        "title": "Quality Assurance & Operations Coordinator",
        "description": """We are looking for a detail-oriented Quality Assurance professional to maintain operational standards.

Responsibilities:
- Monitor and evaluate operational processes and service quality
- Develop and implement quality control procedures and standards
- Conduct audits, inspections, and quality assessments
- Analyze customer feedback and resolve service quality issues
- Prepare quality reports and present findings to management
- Coordinate with operations teams to improve workflow efficiency
- Train staff on quality standards and compliance requirements

Requirements:
- 2+ years of experience in quality control, quality assurance, or operations
- Strong analytical and problem-solving skills
- Knowledge of quality management systems and standards
- Experience with administrative operations and reporting
- Proficiency in Microsoft Office (Excel, Word)
- Attention to detail and process-oriented mindset
- Good communication and team coordination skills

Nice to have:
- ISO or quality management certification
- Experience in customer service quality monitoring
- Knowledge of UAE regulatory standards
- Arabic language proficiency""",
        "min_experience": 2.0,
        "education_required": "Associate",
    },
    {
        "title": "Call Center Team Leader / Customer Experience Manager",
        "description": """We are seeking an experienced Call Center Team Leader to manage our customer service operations.

Responsibilities:
- Lead and supervise call center agents and customer service teams
- Monitor call quality, resolve escalations, and ensure KPI achievement
- Coach and develop team members through regular feedback and training
- Manage multi-channel customer inquiries (phone, email, chat, in-person)
- Prepare daily/weekly performance reports and dashboards
- Implement process improvements to enhance customer satisfaction
- Coordinate with branch operations and retail teams

Requirements:
- 5+ years of customer service or call center experience, including team leadership
- Proven track record in achieving customer satisfaction targets
- Strong leadership, coaching, and people management skills
- Excellent communication and conflict resolution abilities
- Experience with CRM systems and customer service tools
- Ability to handle escalations and high-pressure environments
- Quality assurance and performance monitoring experience

Nice to have:
- Experience in UAE retail, banking, or telecom call centers
- Knowledge of Amadeus, Galileo, or reservation systems
- Bilingual Arabic/English
- Customer experience management certification""",
        "min_experience": 5.0,
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
