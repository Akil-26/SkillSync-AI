"""
Sample candidate data for testing.

These fixtures represent a realistic spread of candidate types:
- Strong match, weak match, disqualified, honeypot, edge cases.
"""

SAMPLE_JD = {
    "title": "Senior Python Backend Engineer",
    "full_text": (
        "Senior Python Backend Engineer\n"
        "We are looking for an experienced Python backend engineer to join our "
        "platform team. You will design and build scalable microservices, work "
        "with databases, and deploy to cloud infrastructure.\n"
        "Must Have\n"
        "5+ years of professional software development experience\n"
        "Strong proficiency in Python\n"
        "Experience with REST APIs and microservices architecture\n"
        "Required Skills\n"
        "Python, Django, PostgreSQL, Docker, REST API, Git\n"
        "Nice to Have\n"
        "Experience with Kubernetes, AWS, CI/CD pipelines\n"
        "Responsibilities\n"
        "Design and implement backend services\n"
        "Write clean, testable, production-grade code\n"
        "Collaborate with frontend and data teams"
    ),
    "must_have_requirements": [
        "5+ years of professional software development experience",
        "Strong proficiency in Python",
        "Experience with REST APIs and microservices architecture",
    ],
    "nice_to_have": [
        "Experience with Kubernetes, AWS, CI/CD pipelines",
    ],
    "responsibilities": [
        "Design and implement backend services",
        "Write clean, testable, production-grade code",
        "Collaborate with frontend and data teams",
    ],
    "required_skills": [
        "Python", "Django", "PostgreSQL", "Docker", "REST API", "Git",
    ],
    "min_experience_years": 5.0,
}


SAMPLE_CANDIDATES = [
    {
        # Strong match — experienced, all required skills, clean history
        "candidate_id": "C001",
        "full_name": "Alice Chen",
        "email": "alice.chen@gmail.com",
        "resume_text": (
            "Experienced Python backend engineer with 8 years of building "
            "scalable microservices using Django and Flask. Expert in PostgreSQL "
            "database design, Docker containerization, and REST API development. "
            "Led a team of 5 engineers at TechCorp to redesign the payments "
            "platform, reducing latency by 40%. Proficient with Git, CI/CD "
            "pipelines, and AWS infrastructure."
        ),
        "skills": ["Python", "Django", "Flask", "PostgreSQL", "Docker",
                   "REST API", "Git", "AWS", "CI/CD", "Kubernetes"],
        "total_experience_years": 8,
        "current_title": "Senior Backend Engineer",
        "past_titles": ["Backend Engineer", "Software Engineer"],
        "companies": ["TechCorp", "StartupXYZ", "BigCo"],
        "education": [{"degree": "B.S. Computer Science", "school": "MIT"}],
        "certifications": ["AWS Solutions Architect"],
        "work_authorization": True,
        "location": "San Francisco, CA",
        "projects": [
            {"name": "Payment Platform Redesign", "tech": ["Python", "Django", "PostgreSQL"]},
        ],
        "employment_history": [
            {"start_date": "2020-01-15", "end_date": None, "title": "Senior Backend Engineer"},
            {"start_date": "2017-06-01", "end_date": "2019-12-31", "title": "Backend Engineer"},
            {"start_date": "2015-09-01", "end_date": "2017-05-15", "title": "Software Engineer"},
        ],
        "expected_salary": 180000,
        "notice_period_days": 30,
    },
    {
        # Decent match — mid-level, some skills missing
        "candidate_id": "C002",
        "full_name": "Bob Martinez",
        "email": "bob.martinez@outlook.com",
        "resume_text": (
            "Software developer with 6 years of experience in Python and "
            "JavaScript. Built REST APIs using FastAPI and Express.js. "
            "Familiar with MySQL and MongoDB databases. Experience with "
            "Docker and basic cloud deployments on GCP."
        ),
        "skills": ["Python", "JavaScript", "FastAPI", "Docker", "REST API",
                   "MySQL", "MongoDB", "Git", "GCP"],
        "total_experience_years": 6,
        "current_title": "Software Developer",
        "past_titles": ["Junior Developer", "Intern"],
        "companies": ["MidCorp", "SmallStartup"],
        "education": [{"degree": "B.S. Computer Science", "school": "State University"}],
        "certifications": [],
        "work_authorization": True,
        "location": "Austin, TX",
        "projects": [],
        "employment_history": [
            {"start_date": "2021-03-01", "end_date": None, "title": "Software Developer"},
            {"start_date": "2018-08-01", "end_date": "2021-02-15", "title": "Junior Developer"},
            {"start_date": "2017-06-01", "end_date": "2018-07-31", "title": "Intern"},
        ],
        "expected_salary": 140000,
        "notice_period_days": 14,
    },
    {
        # Disqualified — too few years of experience
        "candidate_id": "C003",
        "full_name": "Carol White",
        "email": "carol.white@yahoo.com",
        "resume_text": (
            "Recent computer science graduate with 2 years of experience. "
            "Worked on Django web applications and basic REST APIs. "
            "Eager to learn and grow in a backend engineering role. "
            "Completed several online courses on Python and databases."
        ),
        "skills": ["Python", "Django", "REST API", "Git", "HTML", "CSS"],
        "total_experience_years": 2,
        "current_title": "Junior Developer",
        "past_titles": [],
        "companies": ["FirstJob Inc"],
        "education": [{"degree": "B.S. Computer Science", "school": "Community College"}],
        "certifications": [],
        "work_authorization": True,
        "location": "Denver, CO",
        "projects": [],
        "employment_history": [
            {"start_date": "2023-06-01", "end_date": None, "title": "Junior Developer"},
        ],
        "expected_salary": 85000,
        "notice_period_days": 14,
    },
    {
        # Honeypot — suspicious profile (keyword stuffing, fake email, excessive skills)
        "candidate_id": "C004",
        "full_name": "Dave Fraud",
        "email": "dave@mailinator.com",
        "resume_text": (
            "Python Python Python Python Python Python Python Python Python Python "
            "Python Python Python Python Python Python Python Python Python Python "
            "Django Django Django Django Django Django Django Django Django Django "
            "Expert Expert Expert Expert Expert Expert Expert Expert Expert Expert "
            "Senior Senior Senior Senior Senior Senior Senior Senior Senior Senior"
        ),
        "skills": [
            "Python", "Java", "C++", "C#", "Ruby", "Go", "Rust", "Scala",
            "Kotlin", "Swift", "Objective-C", "PHP", "Perl", "R", "MATLAB",
            "Haskell", "Erlang", "Clojure", "F#", "TypeScript", "JavaScript",
            "HTML", "CSS", "SQL", "NoSQL", "GraphQL", "REST", "SOAP", "gRPC",
            "Django", "Flask", "FastAPI", "Spring", "Rails", "Express", "React",
            "Angular", "Vue", "Svelte", "Next.js", "Node.js", "Docker",
            "Kubernetes", "Terraform", "Ansible", "Jenkins", "CircleCI",
            "AWS", "GCP", "Azure", "Heroku", "DigitalOcean", "Linux",
            "Windows", "macOS", "Git", "SVN", "Mercurial", "PostgreSQL",
            "MySQL", "MongoDB", "Redis", "Elasticsearch", "Kafka",
            "RabbitMQ", "Spark", "Hadoop", "TensorFlow", "PyTorch",
        ],
        "total_experience_years": 50,
        "current_title": "Principal Staff Architect",
        "past_titles": ["CTO", "VP Engineering", "Director", "Staff Engineer"],
        "companies": [],
        "education": [],
        "certifications": [],
        "work_authorization": True,
        "location": "Anywhere",
        "projects": [],
        "employment_history": [],
        "expected_salary": 500000,
        "notice_period_days": 0,
    },
    {
        # Edge case — decent candidate but job hopper
        "candidate_id": "C005",
        "full_name": "Eve Hopper",
        "email": "eve.hopper@protonmail.com",
        "resume_text": (
            "Backend developer with 7 years of experience across multiple "
            "companies. Strong Python skills with experience in Django and "
            "PostgreSQL. Have worked with Docker and Git extensively. "
            "Quick learner who adapts to new environments rapidly."
        ),
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "Git",
                   "REST API", "Redis"],
        "total_experience_years": 7,
        "current_title": "Backend Developer",
        "past_titles": ["Developer", "Engineer", "Junior Dev", "Backend Dev", "API Dev"],
        "companies": ["Co1", "Co2", "Co3", "Co4", "Co5", "Co6", "Co7", "Co8"],
        "education": [{"degree": "B.S. CS", "school": "Online University"}],
        "certifications": [],
        "work_authorization": True,
        "location": "Remote",
        "projects": [],
        "employment_history": [
            {"start_date": "2024-06-01", "end_date": None, "title": "Backend Developer"},
            {"start_date": "2024-01-01", "end_date": "2024-05-15", "title": "Developer"},
            {"start_date": "2023-04-01", "end_date": "2023-12-15", "title": "Engineer"},
            {"start_date": "2022-09-01", "end_date": "2023-03-15", "title": "Backend Dev"},
            {"start_date": "2022-01-01", "end_date": "2022-08-15", "title": "API Dev"},
            {"start_date": "2020-06-01", "end_date": "2021-12-15", "title": "Developer"},
            {"start_date": "2019-03-01", "end_date": "2020-05-15", "title": "Junior Dev"},
            {"start_date": "2018-01-01", "end_date": "2019-02-15", "title": "Junior Dev"},
        ],
        "expected_salary": 150000,
        "notice_period_days": 7,
    },
]
