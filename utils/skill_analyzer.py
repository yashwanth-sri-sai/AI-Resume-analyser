"""
utils/skill_analyzer.py
Skill gap analysis: maps resume skills to job requirements and suggests resources.
"""

import json
import os
from typing import Optional


LEARNING_RESOURCES = {
    "Python": {"platform": "Coursera", "url": "https://coursera.org/learn/python"},
    "JavaScript": {"platform": "freeCodeCamp", "url": "https://freecodecamp.org/learn/javascript-algorithms-and-data-structures"},
    "TypeScript": {"platform": "TypeScript Docs", "url": "https://typescriptlang.org/docs"},
    "React": {"platform": "React Docs", "url": "https://react.dev/learn"},
    "AWS": {"platform": "AWS Training", "url": "https://aws.amazon.com/training"},
    "Docker": {"platform": "Docker Docs", "url": "https://docs.docker.com/get-started"},
    "Kubernetes": {"platform": "Kubernetes Docs", "url": "https://kubernetes.io/docs/tutorials"},
    "Machine Learning": {"platform": "Coursera (Andrew Ng)", "url": "https://coursera.org/learn/machine-learning"},
    "Deep Learning": {"platform": "fast.ai", "url": "https://course.fast.ai"},
    "SQL": {"platform": "SQLZoo", "url": "https://sqlzoo.net"},
    "PostgreSQL": {"platform": "PostgreSQL Tutorial", "url": "https://postgresql.org/docs/current/tutorial.html"},
    "MongoDB": {"platform": "MongoDB University", "url": "https://university.mongodb.com"},
    "Git": {"platform": "Git SCM", "url": "https://git-scm.com/book"},
    "Django": {"platform": "Django Docs", "url": "https://docs.djangoproject.com/en/stable/intro"},
    "Flask": {"platform": "Flask Docs", "url": "https://flask.palletsprojects.com"},
    "FastAPI": {"platform": "FastAPI Docs", "url": "https://fastapi.tiangolo.com/tutorial"},
    "TensorFlow": {"platform": "TensorFlow Tutorials", "url": "https://tensorflow.org/tutorials"},
    "PyTorch": {"platform": "PyTorch Tutorials", "url": "https://pytorch.org/tutorials"},
    "scikit-learn": {"platform": "scikit-learn Docs", "url": "https://scikit-learn.org/stable/user_guide.html"},
    "Node.js": {"platform": "Node.js Docs", "url": "https://nodejs.dev/learn"},
    "Java": {"platform": "Codecademy", "url": "https://codecademy.com/learn/learn-java"},
    "Go": {"platform": "Go Tour", "url": "https://go.dev/tour/welcome/1"},
    "Kubernetes": {"platform": "CNCF", "url": "https://kubernetes.io/docs/tutorials/hello-minikube"},
    "Agile": {"platform": "Scrum.org", "url": "https://scrum.org/resources/what-is-scrum"},
    "CI/CD": {"platform": "GitHub Actions Docs", "url": "https://docs.github.com/actions"},
    "Linux": {"platform": "Linux Foundation", "url": "https://linuxfoundation.org/training/linux"},
}

# Skill category groupings
SKILL_CATEGORIES = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
        "Swift", "Kotlin", "Ruby", "PHP", "Scala", "R", "Bash",
    ],
    "Web Frameworks": [
        "React", "Angular", "Vue", "Next.js", "Nuxt.js", "Node.js", "Express",
        "Django", "Flask", "FastAPI", "Spring", "Rails", "Laravel",
    ],
    "Databases": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
        "DynamoDB", "Cassandra", "SQLite", "Oracle", "SQL Server",
    ],
    "Cloud & DevOps": [
        "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "Ansible",
        "CI/CD", "Jenkins", "GitHub Actions", "GitLab CI", "Heroku", "Linux",
    ],
    "Data & AI/ML": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy",
        "Data Analysis", "Power BI", "Tableau", "Spark", "Hadoop",
    ],
    "APIs & Architecture": [
        "REST API", "GraphQL", "gRPC", "Microservices", "WebSocket", "OAuth", "JWT",
    ],
    "Frontend & Design": [
        "HTML", "CSS", "Sass", "Tailwind", "Bootstrap", "Figma", "UI/UX", "Webpack", "Vite",
    ],
    "Tools & Soft Skills": [
        "Git", "GitHub", "GitLab", "JIRA", "Agile", "Scrum", "Problem Solving",
        "Leadership", "Communication", "Teamwork",
    ],
}


def categorize_skills(skills: list) -> dict:
    """Group skills by category."""
    categorized = {cat: [] for cat in SKILL_CATEGORIES}
    categorized["Other"] = []

    for skill in skills:
        placed = False
        for cat, cat_skills in SKILL_CATEGORIES.items():
            if any(skill.lower() == s.lower() for s in cat_skills):
                categorized[cat].append(skill)
                placed = True
                break
        if not placed:
            categorized["Other"].append(skill)

    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}


def analyze_skill_gap(resume_skills: list, job_skills: list) -> dict:
    """
    Analyze the skill gap between resume skills and job requirements.

    Returns:
        - matched_skills: Skills the candidate has that match job requirements
        - missing_skills: Required skills the candidate is missing
        - match_percentage: Percentage of job skills the candidate has
        - recommendations: Learning resources for missing skills
    """
    resume_set = {s.lower(): s for s in resume_skills}
    job_set = {s.lower(): s for s in job_skills}

    matched = []
    missing = []

    for skill_lower, skill_orig in job_set.items():
        if skill_lower in resume_set:
            matched.append(resume_set[skill_lower])
        else:
            missing.append(skill_orig)

    match_percentage = round((len(matched) / max(len(job_skills), 1)) * 100)

    # Generate learning recommendations for missing skills
    recommendations = []
    for skill in missing[:10]:  # Top 10 missing skills
        resource = LEARNING_RESOURCES.get(skill, {
            "platform": "Udemy",
            "url": f"https://udemy.com/courses/search/?q={skill.replace(' ', '+')}",
        })
        recommendations.append({
            "skill": skill,
            "platform": resource["platform"],
            "url": resource["url"],
        })

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": match_percentage,
        "total_job_skills": len(job_skills),
        "total_resume_skills": len(resume_skills),
        "recommendations": recommendations,
    }


def get_skill_strength(skills: list) -> dict:
    """
    Estimate the overall skill profile strength.
    Returns a dict with strength score and category breakdown.
    """
    categorized = categorize_skills(skills)

    total_skills = len(skills)
    covered_categories = len(categorized)
    total_categories = len(SKILL_CATEGORIES)

    # Bonus for breadth across categories
    breadth_score = round((covered_categories / total_categories) * 100)

    # Depth score based on skills per category
    depth_score = min(total_skills * 3, 100)

    overall = round((breadth_score + depth_score) / 2)

    return {
        "overall_strength": overall,
        "breadth_score": breadth_score,
        "depth_score": min(depth_score, 100),
        "categories_covered": covered_categories,
        "total_skills": total_skills,
        "by_category": {cat: len(skills) for cat, skills in categorized.items()},
    }
