"""
utils/text_processor.py
Resume text processing: section detection, cleaning, NLP preprocessing.
"""

import re
from typing import Optional


# Section header patterns
SECTION_PATTERNS = {
    "contact": [
        r"\b(contact|personal\s+info|personal\s+details|address|phone|email)\b"
    ],
    "summary": [
        r"\b(summary|objective|profile|about\s+me|professional\s+summary|career\s+objective)\b"
    ],
    "experience": [
        r"\b(experience|work\s+experience|employment|professional\s+experience|work\s+history|career\s+history)\b"
    ],
    "education": [
        r"\b(education|academic|qualification|degree|university|college|school)\b"
    ],
    "skills": [
        r"\b(skills|technical\s+skills|core\s+competencies|competencies|expertise|technologies)\b"
    ],
    "projects": [
        r"\b(projects|personal\s+projects|key\s+projects|portfolio)\b"
    ],
    "certifications": [
        r"\b(certifications?|certificates?|licenses?|credentials?|courses?)\b"
    ],
    "awards": [
        r"\b(awards?|achievements?|honors?|recognition|accomplishments?)\b"
    ],
    "publications": [
        r"\b(publications?|papers?|research|articles?)\b"
    ],
    "languages": [
        r"\b(languages?|spoken\s+languages?)\b"
    ],
    "volunteer": [
        r"\b(volunteer|volunteering|community\s+service)\b"
    ],
    "references": [
        r"\b(references?)\b"
    ],
}


def clean_text(text: str) -> str:
    """Clean and normalize resume text."""
    # Remove excessive whitespace
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    # Remove special unicode chars
    text = text.encode("ascii", errors="ignore").decode("ascii")
    return text.strip()


def detect_sections(text: str) -> dict:
    """
    Detect resume sections and return a dict mapping section names to their content.
    """
    lines = text.split("\n")
    sections = {}
    current_section = "header"
    current_content = []

    for line in lines:
        line_lower = line.lower().strip()
        detected_section = None

        if len(line_lower) < 60:  # Section headers are usually short
            for section_name, patterns in SECTION_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, line_lower):
                        detected_section = section_name
                        break
                if detected_section:
                    break

        if detected_section:
            # Save current section
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = detected_section
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def extract_contact_info(text: str) -> dict:
    """Extract contact information from resume text."""
    contact = {}

    # Email
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    contact["email"] = emails[0] if emails else None

    # Phone
    phone_pattern = r"(\+?\d[\d\s\-\(\)]{8,}\d)"
    phones = re.findall(phone_pattern, text)
    contact["phone"] = phones[0].strip() if phones else None

    # LinkedIn
    linkedin_pattern = r"linkedin\.com/in/[\w\-]+"
    linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
    contact["linkedin"] = linkedin[0] if linkedin else None

    # GitHub
    github_pattern = r"github\.com/[\w\-]+"
    github = re.findall(github_pattern, text, re.IGNORECASE)
    contact["github"] = github[0] if github else None

    # Website/Portfolio
    website_pattern = r"https?://(?!linkedin|github)[\w\-\.]+\.\w{2,}"
    websites = re.findall(website_pattern, text, re.IGNORECASE)
    contact["website"] = websites[0] if websites else None

    return contact


def extract_years_of_experience(text: str) -> int:
    """Estimate years of experience from dates in resume."""
    year_pattern = r"\b(19|20)\d{2}\b"
    years_found = [int(y) for y in re.findall(year_pattern, text)]

    if not years_found:
        return 0

    min_year = min(years_found)
    max_year = max(years_found)

    # Sanity check
    import datetime
    current_year = datetime.datetime.now().year
    if min_year < 1960 or max_year > current_year + 1:
        return 0

    return max(0, max_year - min_year)


def count_action_verbs(text: str) -> int:
    """Count strong action verbs commonly used in resumes."""
    action_verbs = {
        "achieved", "built", "created", "designed", "developed", "directed",
        "established", "executed", "generated", "implemented", "improved",
        "increased", "launched", "led", "managed", "optimized", "produced",
        "reduced", "resolved", "spearheaded", "streamlined", "trained",
        "transformed", "utilized", "delivered", "deployed", "engineered",
        "collaborated", "coordinated", "automated", "analyzed", "architected",
        "negotiated", "mentored", "oversaw", "planned", "presented", "processed",
    }
    text_words = set(re.findall(r"\b\w+\b", text.lower()))
    return len(action_verbs.intersection(text_words))


def count_quantifications(text: str) -> int:
    """Count quantified achievements (numbers, percentages, dollar amounts)."""
    patterns = [
        r"\d+%",           # Percentages
        r"\$[\d,]+",       # Dollar amounts
        r"\d+[KMBx]",      # Numbers with suffixes
        r"\b\d{4,}\b",     # Large numbers (4+ digits)
        r"\d+\s*(million|billion|thousand)",  # Written amounts
    ]
    total = 0
    for pattern in patterns:
        total += len(re.findall(pattern, text, re.IGNORECASE))
    return total


def extract_skills_from_text(text: str, skills_db: Optional[list] = None) -> list:
    """Extract skills mentioned in the resume text."""
    if skills_db is None:
        # Default common tech skills
        skills_db = [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI", "Spring",
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "CI/CD",
            "Git", "GitHub", "GitLab", "Jenkins", "Linux", "Bash",
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
            "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy",
            "REST API", "GraphQL", "Microservices", "Agile", "Scrum", "JIRA",
            "HTML", "CSS", "Tailwind", "Bootstrap", "Figma", "UI/UX",
            "Data Analysis", "Power BI", "Tableau", "Excel", "R",
        ]

    found_skills = []
    text_lower = text.lower()
    for skill in skills_db:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return list(set(found_skills))


def get_resume_summary_stats(text: str) -> dict:
    """Get high-level statistics about the resume."""
    sections = detect_sections(text)
    contact = extract_contact_info(text)

    return {
        "word_count": len(text.split()),
        "char_count": len(text),
        "sections_found": list(sections.keys()),
        "section_count": len(sections),
        "has_email": contact["email"] is not None,
        "has_phone": contact["phone"] is not None,
        "has_linkedin": contact["linkedin"] is not None,
        "has_github": contact["github"] is not None,
        "action_verb_count": count_action_verbs(text),
        "quantification_count": count_quantifications(text),
        "estimated_experience_years": extract_years_of_experience(text),
        "contact_info": contact,
        "sections": sections,
    }
