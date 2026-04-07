"""
utils/keyword_extractor.py
TF-IDF based keyword extraction and keyword gap analysis.
"""

import re
from collections import Counter
from typing import Optional


def tokenize(text: str) -> list:
    """Simple word tokenizer."""
    tokens = re.findall(r"\b[a-z][a-z\+\#\.]{1,}\b", text.lower())
    return tokens


STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "can", "this", "that", "these", "those",
    "i", "you", "he", "she", "we", "they", "my", "your", "his", "her", "its",
    "our", "their", "as", "if", "then", "than", "when", "where", "who", "which",
    "what", "how", "all", "each", "every", "both", "few", "more", "most",
    "other", "some", "such", "no", "not", "only", "same", "so", "very",
    "just", "also", "any", "because", "while", "through", "during", "before",
    "after", "above", "below", "between", "into", "out", "up", "about",
    "work", "experience", "skills", "years", "using", "ability", "strong",
    "knowledge", "including", "well", "position", "team", "company",
    "good", "new", "client", "role", "candidate", "looking", "responsibilities",
}


def extract_keywords(text: str, top_n: int = 30) -> list:
    """
    Extract top keywords from text using term frequency.
    Returns list of (word, frequency) tuples.
    """
    tokens = tokenize(text)
    # Filter stop words and short/long words
    tokens = [t for t in tokens if t not in STOP_WORDS and 3 <= len(t) <= 20]

    freq = Counter(tokens)
    return freq.most_common(top_n)


def extract_bigrams(text: str, top_n: int = 15) -> list:
    """
    Extract meaningful bigrams (two-word phrases).
    Returns list of (bigram, frequency) tuples.
    """
    tokens = tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS]

    bigrams = []
    for i in range(len(tokens) - 1):
        bigrams.append(f"{tokens[i]} {tokens[i+1]}")

    freq = Counter(bigrams)
    return freq.most_common(top_n)


def keyword_match_analysis(resume_text: str, job_description: str) -> dict:
    """
    Compare resume keywords against job description keywords.

    Returns:
        - match_score: 0-100
        - matched_keywords: keywords present in both
        - missing_keywords: keywords in JD but not in resume
        - extra_keywords: keywords in resume not in JD
    """
    resume_keywords = set(kw for kw, _ in extract_keywords(resume_text, top_n=50))
    jd_keywords = set(kw for kw, _ in extract_keywords(job_description, top_n=50))

    matched = resume_keywords.intersection(jd_keywords)
    missing = jd_keywords - resume_keywords
    extra = resume_keywords - jd_keywords

    match_score = round((len(matched) / max(len(jd_keywords), 1)) * 100)

    return {
        "match_score": match_score,
        "matched_keywords": sorted(list(matched)),
        "missing_keywords": sorted(list(missing)),
        "extra_keywords": sorted(list(extra)),
        "total_jd_keywords": len(jd_keywords),
        "total_resume_keywords": len(resume_keywords),
        "total_matched": len(matched),
    }


def extract_tech_skills_from_jd(jd_text: str) -> list:
    """Extract technology/tool mentions from a job description."""
    tech_patterns = [
        r"\b(Python|JavaScript|TypeScript|Java|C\+\+|C#|Go|Rust|Swift|Kotlin|Ruby|PHP|Scala|R)\b",
        r"\b(React|Angular|Vue|Next\.js|Node\.js|Express|Django|Flask|FastAPI|Spring|Rails|Laravel)\b",
        r"\b(MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch|DynamoDB|Cassandra|SQLite|Oracle|SQL Server)\b",
        r"\b(AWS|GCP|Azure|Heroku|Vercel|Netlify|DigitalOcean|Cloudflare)\b",
        r"\b(Docker|Kubernetes|Terraform|Ansible|Jenkins|CircleCI|GitHub Actions|GitLab CI|ArgoCD)\b",
        r"\b(TensorFlow|PyTorch|scikit-learn|pandas|NumPy|Spark|Hadoop|Kafka|Airflow)\b",
        r"\b(REST|GraphQL|gRPC|WebSocket|OAuth|JWT|OpenAPI|Swagger)\b",
        r"\b(HTML|CSS|Sass|Tailwind|Bootstrap|Webpack|Vite|Babel)\b",
        r"\b(Git|GitHub|GitLab|Bitbucket|Jira|Confluence|Slack|Notion)\b",
        r"\b(Linux|Unix|Bash|PowerShell|Shell)\b",
    ]

    found = set()
    for pattern in tech_patterns:
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        found.update(matches)

    return sorted(list(found))
