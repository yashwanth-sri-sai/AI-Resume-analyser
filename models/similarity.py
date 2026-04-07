"""
models/similarity.py
TF-IDF based cosine similarity engine for resume-to-job matching.
"""

from typing import Optional
import re


def compute_tfidf_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using TF-IDF.
    Returns a score from 0.0 to 100.0.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=1000,
        )

        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return round(float(similarity[0][0]) * 100, 1)

    except ImportError:
        return _basic_similarity(text1, text2)
    except Exception:
        return _basic_similarity(text1, text2)


def _basic_similarity(text1: str, text2: str) -> float:
    """Basic similarity using word overlap when sklearn is not available."""
    def tokenize(text):
        return set(re.findall(r"\b[a-z]{3,}\b", text.lower()))

    words1 = tokenize(text1)
    words2 = tokenize(text2)

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return round(len(intersection) / len(union) * 100, 1)


def rank_job_roles(resume_text: str, job_roles: list) -> list:
    """
    Rank a list of job roles by similarity to the resume.

    Args:
        resume_text: The resume text
        job_roles: List of dicts with 'title', 'description', 'required_skills'

    Returns:
        List of job roles sorted by similarity score, highest first
    """
    ranked = []
    for role in job_roles:
        desc = role.get("description", "") + " " + " ".join(role.get("required_skills", []))
        score = compute_tfidf_similarity(resume_text, desc)
        ranked.append({**role, "similarity_score": score})

    ranked.sort(key=lambda x: x["similarity_score"], reverse=True)
    return ranked


def get_semantic_sections(resume_text: str, section_texts: dict) -> dict:
    """
    Score individual resume sections against best practices.
    Returns section quality scores.
    """
    section_benchmarks = {
        "summary": "dynamic professional experienced leader achievement oriented results driven",
        "experience": "developed implemented managed led achieved increased improved reduced built created",
        "skills": "technical proficient experienced expert skilled knowledge tools technologies frameworks",
        "education": "bachelor master degree university college graduated GPA honors distinction",
        "projects": "built created developed designed implemented deployed launched",
    }

    section_scores = {}
    for section, content in section_texts.items():
        if section in section_benchmarks:
            score = compute_tfidf_similarity(content, section_benchmarks[section])
            section_scores[section] = round(score, 1)
        else:
            section_scores[section] = 50.0  # Default neutral score

    return section_scores
