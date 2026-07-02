"""
generate_sample_pipeline.py

Creates synthetic candidates.jsonl.gz + job_description.docx,
runs precompute → rank, then converts predictions to XLSX.

Run with: python generate_sample_pipeline.py
"""
import gzip, json, sys
from pathlib import Path

ROOT = Path(__file__).parent

# ── 1. Write synthetic job_description.docx ───────────────────────────────
def write_jd():
    try:
        # pyrefly: ignore [missing-import]
        import docx
        doc = docx.Document()
        doc.add_heading("Senior Python Backend Engineer", 0)
        doc.add_paragraph(
            "We are looking for an experienced Python backend engineer to join "
            "our platform team. You will design and build scalable microservices, "
            "work with databases, and deploy to cloud infrastructure."
        )
        doc.add_heading("Must Have", 1)
        for item in [
            "5+ years of professional software development experience",
            "Strong proficiency in Python",
            "Experience with REST APIs and microservices architecture",
        ]:
            doc.add_paragraph(item, style="List Bullet")

        doc.add_heading("Required Skills", 1)
        doc.add_paragraph("Python, Django, PostgreSQL, Docker, REST API, Git")

        doc.add_heading("Nice to Have", 1)
        doc.add_paragraph("Kubernetes, AWS, CI/CD pipelines, Redis, FastAPI")

        doc.add_heading("Responsibilities", 1)
        for item in [
            "Design and implement backend microservices",
            "Write clean, testable, production-grade code",
            "Collaborate with frontend and data teams",
            "Perform code reviews and mentor junior engineers",
        ]:
            doc.add_paragraph(item, style="List Bullet")

        out = ROOT / "data" / "job_description.docx"
        doc.save(str(out))
        print(f"[OK] Wrote {out}")
    except Exception as e:
        print(f"[ERROR] JD write failed: {e}")
        sys.exit(1)

# ── 2. Write synthetic candidates.jsonl.gz ────────────────────────────────
CANDIDATES = [
    {
        "candidate_id": "C001",
        "full_name": "Alice Chen",
        "email": "alice.chen@gmail.com",
        "resume_text": (
            "Senior Python backend engineer with 9 years of experience building "
            "scalable microservices. Expert in Django, PostgreSQL, Docker, and REST API design. "
            "Led platform re-architecture at a Series-C fintech reducing p99 latency by 40%. "
            "Proficient with Git, Kubernetes, AWS, and CI/CD. Strong advocate for TDD and code reviews."
        ),
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "REST API", "Git",
                   "Kubernetes", "AWS", "CI/CD", "Redis", "FastAPI"],
        "total_experience_years": 9,
        "current_title": "Senior Backend Engineer",
        "past_titles": ["Backend Engineer", "Software Engineer"],
        "companies": ["FinTechCo", "CloudStartup", "MegaCorp"],
        "education": [{"degree": "B.S. Computer Science", "school": "MIT"}],
        "certifications": ["AWS Solutions Architect"],
        "work_authorization": True,
        "location": "San Francisco, CA",
        "employment_history": [
            {"start_date": "2019-01-15", "end_date": None, "title": "Senior Backend Engineer"},
            {"start_date": "2016-06-01", "end_date": "2018-12-31", "title": "Backend Engineer"},
            {"start_date": "2015-07-01", "end_date": "2016-05-15", "title": "Software Engineer"},
        ],
        "expected_salary": 185000,
        "notice_period_days": 30,
    },
    {
        "candidate_id": "C002",
        "full_name": "Bob Martinez",
        "email": "bob.martinez@outlook.com",
        "resume_text": (
            "Backend developer with 7 years of experience in Python and JavaScript. "
            "Built REST APIs with FastAPI and integrated PostgreSQL and MySQL databases. "
            "Solid Docker and Git knowledge. Led a 3-person backend team at a mid-size SaaS company."
        ),
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API", "Git",
                   "MySQL", "JavaScript", "Node.js"],
        "total_experience_years": 7,
        "current_title": "Backend Developer",
        "past_titles": ["Software Developer", "Junior Developer"],
        "companies": ["SaaSCo", "DevShop"],
        "education": [{"degree": "B.S. Computer Science", "school": "UT Austin"}],
        "certifications": [],
        "work_authorization": True,
        "location": "Austin, TX",
        "employment_history": [
            {"start_date": "2020-03-01", "end_date": None, "title": "Backend Developer"},
            {"start_date": "2017-08-01", "end_date": "2020-02-15", "title": "Software Developer"},
            {"start_date": "2016-06-01", "end_date": "2017-07-31", "title": "Junior Developer"},
        ],
        "expected_salary": 145000,
        "notice_period_days": 14,
    },
    {
        "candidate_id": "C003",
        "full_name": "Carol Patel",
        "email": "carol.patel@protonmail.com",
        "resume_text": (
            "Python engineer with 8 years of experience. Deep expertise in Django REST Framework, "
            "PostgreSQL, and distributed systems. Designed event-driven microservices using Kafka "
            "and Docker/Kubernetes on AWS. Open-source contributor to Django."
        ),
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "REST API", "Git",
                   "Kubernetes", "AWS", "Kafka", "Redis", "CI/CD"],
        "total_experience_years": 8,
        "current_title": "Principal Engineer",
        "past_titles": ["Senior Engineer", "Software Engineer", "Junior Engineer"],
        "companies": ["OpenSourceCo", "CloudBig", "TechStartup"],
        "education": [{"degree": "M.S. Computer Science", "school": "Carnegie Mellon"}],
        "certifications": ["AWS DevOps Engineer"],
        "work_authorization": True,
        "location": "Seattle, WA",
        "employment_history": [
            {"start_date": "2021-01-01", "end_date": None, "title": "Principal Engineer"},
            {"start_date": "2018-04-01", "end_date": "2020-12-31", "title": "Senior Engineer"},
            {"start_date": "2015-09-01", "end_date": "2018-03-31", "title": "Software Engineer"},
        ],
        "expected_salary": 210000,
        "notice_period_days": 45,
    },
    {
        "candidate_id": "C004",
        "full_name": "David Kim",
        "email": "david.kim@yahoo.com",
        "resume_text": (
            "Full-stack developer with 6 years of experience. Primarily React and Node.js "
            "but have worked on Python Flask backends. Comfortable with REST APIs and basic "
            "Docker usage. Looking to transition more fully to backend."
        ),
        "skills": ["Python", "Flask", "REST API", "Docker", "Git", "React", "Node.js",
                   "JavaScript", "MongoDB"],
        "total_experience_years": 6,
        "current_title": "Full Stack Developer",
        "past_titles": ["Frontend Developer", "Web Developer"],
        "companies": ["WebAgency", "DigitalStudio"],
        "education": [{"degree": "B.S. Information Technology", "school": "State University"}],
        "certifications": [],
        "work_authorization": True,
        "location": "Chicago, IL",
        "employment_history": [
            {"start_date": "2021-05-01", "end_date": None, "title": "Full Stack Developer"},
            {"start_date": "2019-01-01", "end_date": "2021-04-30", "title": "Frontend Developer"},
            {"start_date": "2017-08-01", "end_date": "2018-12-31", "title": "Web Developer"},
        ],
        "expected_salary": 130000,
        "notice_period_days": 14,
    },
    {
        "candidate_id": "C005",
        "full_name": "Emma Wilson",
        "email": "emma.wilson@gmail.com",
        "resume_text": (
            "Backend engineer specializing in Python microservices with 5 years experience. "
            "Built Django and FastAPI services with PostgreSQL. Deployed on Docker and familiar "
            "with AWS Lambda and Git workflows. Contributed to internal CI/CD pipeline tooling."
        ),
        "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker", "REST API",
                   "Git", "AWS", "CI/CD"],
        "total_experience_years": 5,
        "current_title": "Backend Engineer",
        "past_titles": ["Software Engineer", "Junior Backend Engineer"],
        "companies": ["MicroSaaS", "StartupHub"],
        "education": [{"degree": "B.S. Computer Science", "school": "Georgia Tech"}],
        "certifications": [],
        "work_authorization": True,
        "location": "Atlanta, GA",
        "employment_history": [
            {"start_date": "2022-02-01", "end_date": None, "title": "Backend Engineer"},
            {"start_date": "2019-08-01", "end_date": "2022-01-15", "title": "Software Engineer"},
            {"start_date": "2018-06-01", "end_date": "2019-07-31", "title": "Junior Backend Engineer"},
        ],
        "expected_salary": 135000,
        "notice_period_days": 21,
    },
    {
        "candidate_id": "C006",
        "full_name": "Frank Zhou",
        "email": "frank.zhou@gmail.com",
        "resume_text": (
            "Data engineer transitioning to backend. 4 years in Python data pipelines "
            "using pandas, PySpark, and Airflow. Some Django experience on side projects. "
            "Familiar with PostgreSQL and Git. Eager to move into product backend engineering."
        ),
        "skills": ["Python", "Django", "PostgreSQL", "Git", "Pandas", "PySpark",
                   "Airflow", "SQL"],
        "total_experience_years": 4,
        "current_title": "Data Engineer",
        "past_titles": ["Junior Data Engineer", "Data Analyst"],
        "companies": ["DataCo", "AnalyticsFirm"],
        "education": [{"degree": "B.S. Statistics", "school": "UCLA"}],
        "certifications": [],
        "work_authorization": True,
        "location": "Los Angeles, CA",
        "employment_history": [
            {"start_date": "2022-06-01", "end_date": None, "title": "Data Engineer"},
            {"start_date": "2020-09-01", "end_date": "2022-05-31", "title": "Junior Data Engineer"},
            {"start_date": "2019-07-01", "end_date": "2020-08-31", "title": "Data Analyst"},
        ],
        "expected_salary": 115000,
        "notice_period_days": 14,
    },
    {
        "candidate_id": "C007",
        "full_name": "Grace Nakamura",
        "email": "grace.nakamura@gmail.com",
        "resume_text": (
            "12 years of backend engineering across e-commerce and fintech. Deep Python expertise "
            "with Django, Django REST Framework, and PostgreSQL at scale (100M+ rows). "
            "Architect of a microservices platform serving 50M users. Experienced with Docker, "
            "Kubernetes, and multi-region AWS deployments. Strong Git, CI/CD, and code review culture."
        ),
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "REST API", "Git",
                   "Kubernetes", "AWS", "CI/CD", "Redis", "FastAPI", "gRPC", "Terraform"],
        "total_experience_years": 12,
        "current_title": "Staff Engineer",
        "past_titles": ["Senior Engineer", "Lead Engineer", "Backend Engineer"],
        "companies": ["EcommGiant", "FintechUnicorn", "TechScale"],
        "education": [{"degree": "M.S. Computer Science", "school": "Stanford"}],
        "certifications": ["AWS Solutions Architect Professional", "CKA"],
        "work_authorization": True,
        "location": "New York, NY",
        "employment_history": [
            {"start_date": "2020-03-01", "end_date": None, "title": "Staff Engineer"},
            {"start_date": "2016-07-01", "end_date": "2020-02-28", "title": "Lead Engineer"},
            {"start_date": "2013-09-01", "end_date": "2016-06-30", "title": "Backend Engineer"},
        ],
        "expected_salary": 250000,
        "notice_period_days": 60,
    },
    {
        "candidate_id": "C008",
        "full_name": "Henry Brooks",
        "email": "henry.brooks@gmail.com",
        "resume_text": (
            "Recent graduate with 1 year of internship experience. Built a Django REST API "
            "as a capstone project. Familiar with Python and basic Git usage. "
            "Enthusiastic about backend development and eager to learn."
        ),
        "skills": ["Python", "Django", "REST API", "Git", "HTML", "CSS"],
        "total_experience_years": 1,
        "current_title": "Junior Developer",
        "past_titles": ["Intern"],
        "companies": ["LocalAgency"],
        "education": [{"degree": "B.S. Computer Science", "school": "Community College"}],
        "certifications": [],
        "work_authorization": True,
        "location": "Denver, CO",
        "employment_history": [
            {"start_date": "2025-06-01", "end_date": None, "title": "Junior Developer"},
            {"start_date": "2024-06-01", "end_date": "2025-05-31", "title": "Intern"},
        ],
        "expected_salary": 80000,
        "notice_period_days": 7,
    },
    {
        "candidate_id": "C009",
        "full_name": "Iris Gomez",
        "email": "iris.gomez@gmail.com",
        "resume_text": (
            "Backend developer with 6 years building Python REST APIs using Flask and FastAPI. "
            "Experienced with PostgreSQL query optimization and Docker-based deployments. "
            "Worked in agile teams with Git, GitHub Actions CI/CD. Strong problem solver."
        ),
        "skills": ["Python", "Flask", "FastAPI", "PostgreSQL", "Docker", "REST API",
                   "Git", "GitHub Actions", "CI/CD", "Redis"],
        "total_experience_years": 6,
        "current_title": "Backend Developer",
        "past_titles": ["Software Developer", "Junior Developer"],
        "companies": ["APICompany", "SoftwareHouse"],
        "education": [{"degree": "B.Eng. Software Engineering", "school": "Arizona State"}],
        "certifications": [],
        "work_authorization": True,
        "location": "Phoenix, AZ",
        "employment_history": [
            {"start_date": "2021-08-01", "end_date": None, "title": "Backend Developer"},
            {"start_date": "2018-03-01", "end_date": "2021-07-31", "title": "Software Developer"},
            {"start_date": "2017-01-01", "end_date": "2018-02-28", "title": "Junior Developer"},
        ],
        "expected_salary": 140000,
        "notice_period_days": 21,
    },
    {
        "candidate_id": "C010",
        "full_name": "Jake Thompson",
        "email": "jake.thompson@gmail.com",
        "resume_text": (
            "DevOps/SRE engineer pivoting to backend. 5 years managing Docker, Kubernetes, "
            "AWS infrastructure and CI/CD pipelines. Python scripting experience with some "
            "Flask service development. Deep understanding of deployment environments "
            "and production reliability."
        ),
        "skills": ["Python", "Flask", "Docker", "Kubernetes", "AWS", "Git", "CI/CD",
                   "REST API", "Terraform", "Linux"],
        "total_experience_years": 5,
        "current_title": "DevOps Engineer",
        "past_titles": ["SRE", "Systems Engineer"],
        "companies": ["CloudOps", "InfraTeam"],
        "education": [{"degree": "B.S. Information Systems", "school": "Penn State"}],
        "certifications": ["AWS DevOps Professional", "CKA"],
        "work_authorization": True,
        "location": "Philadelphia, PA",
        "employment_history": [
            {"start_date": "2022-01-01", "end_date": None, "title": "DevOps Engineer"},
            {"start_date": "2019-06-01", "end_date": "2021-12-31", "title": "SRE"},
            {"start_date": "2018-01-01", "end_date": "2019-05-31", "title": "Systems Engineer"},
        ],
        "expected_salary": 145000,
        "notice_period_days": 30,
    },
]

def write_candidates():
    out = ROOT / "data" / "candidates.jsonl.gz"
    with gzip.open(out, "wt", encoding="utf-8") as f:
        for c in CANDIDATES:
            f.write(json.dumps(c) + "\n")
    print(f"[OK] Wrote {len(CANDIDATES)} candidates to {out}")

if __name__ == "__main__":
    print("[1/2] Writing synthetic data...")
    write_jd()
    write_candidates()
    print("\n[2/2] Done. Now run: python -m src.precompute")
