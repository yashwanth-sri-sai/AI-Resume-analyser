"""
utils/ats_scorer.py
ATS (Applicant Tracking System) scoring algorithm.
Scores resumes on formatting, content quality, and keyword presence.
"""

import re
from typing import Optional


# ATS scoring weights
SCORE_WEIGHTS = {
    "contact_info": 10,      # Has email, phone, LinkedIn
    "section_structure": 15, # Proper sections present
    "content_length": 10,    # Resume length (word count)
    "action_verbs": 10,      # Use of strong action verbs
    "quantification": 15,    # Numbers and metrics in achievements
    "skills_presence": 15,   # Skills section with relevant skills
    "education": 10,         # Education section present
    "experience": 15,        # Work experience present
}


def score_contact_info(stats: dict) -> tuple[int, list]:
    """Score based on contact information completeness."""
    score = 0
    max_score = SCORE_WEIGHTS["contact_info"]
    feedback = []

    if stats.get("has_email"):
        score += 4
    else:
        feedback.append("❌ Missing email address")

    if stats.get("has_phone"):
        score += 3
    else:
        feedback.append("⚠️ Missing phone number")

    if stats.get("has_linkedin"):
        score += 2
    else:
        feedback.append("💡 Add your LinkedIn profile URL")

    if stats.get("has_github"):
        score += 1
    else:
        feedback.append("💡 Consider adding your GitHub profile")

    return score, feedback


def score_section_structure(sections: list) -> tuple[int, list]:
    """Score based on presence of key resume sections."""
    score = 0
    max_score = SCORE_WEIGHTS["section_structure"]
    feedback = []

    essential = ["experience", "education", "skills"]
    recommended = ["summary", "projects", "certifications"]

    for section in essential:
        if section in sections:
            score += 4
        else:
            feedback.append(f"❌ Missing '{section.title()}' section")

    for section in recommended:
        if section in sections:
            score += 1
        else:
            feedback.append(f"💡 Consider adding a '{section.title()}' section")

    return min(score, max_score), feedback


def score_content_length(word_count: int) -> tuple[int, list]:
    """Score based on resume length (ideal: 300-800 words)."""
    score = 0
    max_score = SCORE_WEIGHTS["content_length"]
    feedback = []

    if word_count < 100:
        score = 2
        feedback.append("❌ Resume is too short. Add more detail to your experience and skills.")
    elif word_count < 250:
        score = 5
        feedback.append("⚠️ Resume could be more detailed. Aim for 300-600 words for optimal ATS scoring.")
    elif 300 <= word_count <= 800:
        score = max_score
        feedback.append("✅ Resume length is optimal for ATS systems.")
    elif 250 <= word_count < 300:
        score = 7
        feedback.append("⚠️ Resume is slightly short. Consider expanding your experience descriptions.")
    elif 800 < word_count <= 1200:
        score = 8
        feedback.append("⚠️ Resume is slightly long. Consider condensing to 1 page for entry-level roles.")
    else:
        score = 5
        feedback.append("❌ Resume is too long. ATS systems may truncate long resumes.")

    return score, feedback


def score_action_verbs(action_verb_count: int) -> tuple[int, list]:
    """Score based on use of action verbs."""
    score = 0
    max_score = SCORE_WEIGHTS["action_verbs"]
    feedback = []

    if action_verb_count >= 10:
        score = max_score
        feedback.append("✅ Great use of strong action verbs.")
    elif action_verb_count >= 6:
        score = 7
        feedback.append("⚠️ Use more action verbs (achieved, built, led, managed, etc.).")
    elif action_verb_count >= 3:
        score = 4
        feedback.append("❌ Very few action verbs. Start bullet points with strong verbs.")
    else:
        score = 1
        feedback.append("❌ No strong action verbs detected. Use verbs like: Led, Built, Achieved, Improved...")

    return score, feedback


def score_quantification(quantification_count: int) -> tuple[int, list]:
    """Score based on quantified achievements."""
    score = 0
    max_score = SCORE_WEIGHTS["quantification"]
    feedback = []

    if quantification_count >= 5:
        score = max_score
        feedback.append("✅ Excellent use of quantified achievements.")
    elif quantification_count >= 3:
        score = 10
        feedback.append("⚠️ Good start with metrics. Try to add more numbers to your achievements.")
    elif quantification_count >= 1:
        score = 6
        feedback.append("❌ Very few quantified achievements. Add numbers, percentages, and dollar amounts.")
    else:
        score = 2
        feedback.append("❌ No quantified achievements found. ATS and recruiters prefer: 'Increased sales by 35%'.")

    return score, feedback


def score_skills_section(sections: list, skills_count: int) -> tuple[int, list]:
    """Score based on skills section presence and content."""
    score = 0
    max_score = SCORE_WEIGHTS["skills_presence"]
    feedback = []

    if "skills" in sections:
        score += 5
        if skills_count >= 10:
            score += max_score - 5
            feedback.append("✅ Strong skills section with relevant technologies.")
        elif skills_count >= 5:
            score += 7
            feedback.append("⚠️ Good skills listed. Consider adding more specific technical skills.")
        else:
            score += 3
            feedback.append("❌ Few skills detected. Expand your skills section with specific technologies.")
    else:
        feedback.append("❌ No dedicated Skills section found. ATS systems look for a clear skills list.")
        if skills_count >= 5:
            score += 5
            feedback.append("💡 Skills were found in your text. Create a dedicated section.")

    return min(score, max_score), feedback


def score_education(sections: list) -> tuple[int, list]:
    """Score based on education section presence."""
    score = 0
    max_score = SCORE_WEIGHTS["education"]
    feedback = []

    if "education" in sections:
        score = max_score
        feedback.append("✅ Education section present.")
    else:
        score = 0
        feedback.append("❌ Missing Education section. Always include your educational background.")

    return score, feedback


def score_experience(sections: list, exp_years: int) -> tuple[int, list]:
    """Score based on experience section presence."""
    score = 0
    max_score = SCORE_WEIGHTS["experience"]
    feedback = []

    if "experience" in sections:
        score = max_score
        feedback.append("✅ Work experience section present.")
        if exp_years > 0:
            feedback.append(f"📅 Detected approximately {exp_years} years of experience.")
    else:
        score = 2
        feedback.append("❌ No Work Experience section found. This is critical for ATS systems.")

    return score, feedback


def calculate_ats_score(resume_stats: dict, found_skills: list) -> dict:
    """
    Calculate the full ATS score for a resume.

    Args:
        resume_stats: Output from text_processor.get_resume_summary_stats()
        found_skills: List of skills extracted from the resume

    Returns:
        Dict with total_score, category_scores, all_feedback, grade
    """
    sections = resume_stats.get("sections_found", [])
    word_count = resume_stats.get("word_count", 0)
    action_verbs = resume_stats.get("action_verb_count", 0)
    quantifications = resume_stats.get("quantification_count", 0)
    exp_years = resume_stats.get("estimated_experience_years", 0)

    category_scores = {}
    all_feedback = []

    # Contact Info
    s, f = score_contact_info(resume_stats)
    category_scores["Contact Information"] = {"score": s, "max": SCORE_WEIGHTS["contact_info"]}
    all_feedback.extend(f)

    # Section Structure
    s, f = score_section_structure(sections)
    category_scores["Section Structure"] = {"score": s, "max": SCORE_WEIGHTS["section_structure"]}
    all_feedback.extend(f)

    # Content Length
    s, f = score_content_length(word_count)
    category_scores["Content Length"] = {"score": s, "max": SCORE_WEIGHTS["content_length"]}
    all_feedback.extend(f)

    # Action Verbs
    s, f = score_action_verbs(action_verbs)
    category_scores["Action Verbs"] = {"score": s, "max": SCORE_WEIGHTS["action_verbs"]}
    all_feedback.extend(f)

    # Quantification
    s, f = score_quantification(quantifications)
    category_scores["Quantified Achievements"] = {"score": s, "max": SCORE_WEIGHTS["quantification"]}
    all_feedback.extend(f)

    # Skills
    s, f = score_skills_section(sections, len(found_skills))
    category_scores["Skills Section"] = {"score": s, "max": SCORE_WEIGHTS["skills_presence"]}
    all_feedback.extend(f)

    # Education
    s, f = score_education(sections)
    category_scores["Education"] = {"score": s, "max": SCORE_WEIGHTS["education"]}
    all_feedback.extend(f)

    # Experience
    s, f = score_experience(sections, exp_years)
    category_scores["Work Experience"] = {"score": s, "max": SCORE_WEIGHTS["experience"]}
    all_feedback.extend(f)

    # Calculate total score (out of 100)
    total_score = sum(v["score"] for v in category_scores.values())
    max_possible = sum(v["max"] for v in category_scores.values())
    normalized_score = round((total_score / max_possible) * 100)

    # Assign grade
    if normalized_score >= 90:
        grade = "A+"
        grade_label = "Excellent"
        grade_color = "#10B981"
    elif normalized_score >= 80:
        grade = "A"
        grade_label = "Very Good"
        grade_color = "#34D399"
    elif normalized_score >= 70:
        grade = "B"
        grade_label = "Good"
        grade_color = "#FBBF24"
    elif normalized_score >= 60:
        grade = "C"
        grade_label = "Average"
        grade_color = "#F97316"
    elif normalized_score >= 50:
        grade = "D"
        grade_label = "Below Average"
        grade_color = "#EF4444"
    else:
        grade = "F"
        grade_label = "Needs Major Improvement"
        grade_color = "#DC2626"

    return {
        "total_score": normalized_score,
        "grade": grade,
        "grade_label": grade_label,
        "grade_color": grade_color,
        "category_scores": category_scores,
        "feedback": all_feedback,
        "improvements": [f for f in all_feedback if f.startswith("❌") or f.startswith("⚠️")],
        "positives": [f for f in all_feedback if f.startswith("✅")],
    }
