"""
utils/llm_client.py
Gemini API client wrapper with prompt templates for resume analysis.
"""

import os
import json
from typing import Optional


def get_gemini_client():
    """Initialize and return the Gemini client."""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        return genai
    except ImportError:
        return None


def analyze_resume_with_ai(resume_text: str, ats_score: int, skills: list) -> dict:
    """
    Use Gemini to deeply analyze a resume and provide actionable suggestions.

    Returns:
        - overall_assessment: string
        - strengths: list of strings
        - improvements: list of strings
        - rewrite_tips: list of strings
        - career_level: string
        - suggested_roles: list of strings
    """
    genai = get_gemini_client()
    if genai is None:
        return _mock_ai_analysis(ats_score, skills)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are an expert resume coach and ATS specialist with 15 years of experience.

Analyze the following resume and provide specific, actionable feedback.

Resume Text:
---
{resume_text[:3000]}
---

Current ATS Score: {ats_score}/100
Detected Skills: {', '.join(skills[:20])}

Please provide your analysis in the following JSON format:
{{
  "overall_assessment": "2-3 sentence overall assessment",
  "career_level": "Entry/Mid/Senior/Executive",
  "suggested_roles": ["role1", "role2", "role3"],
  "strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2", "improvement3", "improvement4"],
  "rewrite_tips": ["tip1", "tip2", "tip3"],
  "summary_rewrite": "A suggested professional summary rewrite (2-3 sentences)"
}}

Respond ONLY with the JSON object, no extra text."""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Extract JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)
        result["ai_powered"] = True
        return result

    except Exception as e:
        return _mock_ai_analysis(ats_score, skills)


def match_resume_to_job(resume_text: str, job_description: str, match_score: float) -> dict:
    """
    Use Gemini to analyze resume-to-job fit and provide specific gap analysis.
    """
    genai = get_gemini_client()
    if genai is None:
        return _mock_job_match(match_score)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are an expert recruiter and career coach.

Analyze how well this resume matches the job description.

Resume (excerpt):
---
{resume_text[:2000]}
---

Job Description:
---
{job_description[:2000]}
---

Keyword Match Score: {match_score}%

Provide analysis in JSON format:
{{
  "fit_assessment": "2-3 sentence assessment of overall fit",
  "match_percentage": {match_score},
  "top_matching_points": ["point1", "point2", "point3"],
  "critical_gaps": ["gap1", "gap2", "gap3"],
  "cover_letter_tips": ["tip1", "tip2"],
  "interview_prep_topics": ["topic1", "topic2", "topic3"],
  "should_apply": true/false,
  "confidence_level": "Low/Medium/High"
}}

Respond ONLY with the JSON object."""

        response = model.generate_content(prompt)
        text = response.text.strip()

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)
        result["ai_powered"] = True
        return result

    except Exception as e:
        return _mock_job_match(match_score)


def chat_with_resume(resume_text: str, conversation_history: list, user_message: str) -> str:
    """
    Chat interface: answer questions about the resume.
    """
    genai = get_gemini_client()
    if genai is None:
        return _mock_chat_response(user_message)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Build conversation context
        history_text = ""
        for msg in conversation_history[-6:]:  # Last 6 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

        prompt = f"""You are an expert career coach and resume advisor helping a candidate improve their resume.

You have access to their resume:
---
{resume_text[:3000]}
---

Previous conversation:
{history_text}

User's new message: {user_message}

Respond as a helpful, professional career coach. Be specific, actionable, and encouraging.
Keep your response concise (2-4 paragraphs max)."""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return _mock_chat_response(user_message)


def _mock_ai_analysis(ats_score: int, skills: list) -> dict:
    """Mock AI analysis for when API key is not available."""
    return {
        "overall_assessment": f"Your resume has an ATS score of {ats_score}/100. It shows a solid foundation with {len(skills)} detected skills. There are several areas where targeted improvements could significantly boost your visibility with recruiters.",
        "career_level": "Mid-Level" if ats_score > 60 else "Entry-Level",
        "suggested_roles": ["Software Developer", "Backend Engineer", "Full-Stack Developer"],
        "strengths": [
            "Technical skills are clearly listed",
            "Resume follows a logical structure",
            "Relevant experience is documented",
        ],
        "improvements": [
            "Add more quantified achievements (numbers, percentages, impact)",
            "Include a compelling professional summary at the top",
            "Tailor keywords to match specific job descriptions",
            "Add more action verbs to bullet points",
        ],
        "rewrite_tips": [
            "Start each bullet point with a strong action verb",
            "Include metrics: 'Improved performance by 40%' instead of 'Improved performance'",
            "Add links to GitHub, portfolio, or relevant projects",
        ],
        "summary_rewrite": "Results-driven professional with experience in software development and a track record of delivering high-quality solutions. Skilled in modern technologies with a passion for continuous learning and innovation.",
        "ai_powered": False,
    }


def _mock_job_match(match_score: float) -> dict:
    """Mock job match for when API key is not available."""
    should_apply = match_score >= 50
    return {
        "fit_assessment": f"Based on keyword analysis, your resume matches approximately {match_score:.0f}% of the job requirements. {'You are a strong candidate for this role.' if should_apply else 'Consider upskilling in the missing areas before applying.'}",
        "match_percentage": match_score,
        "top_matching_points": [
            "Technical skills align with job requirements",
            "Experience level appropriate for the role",
        ],
        "critical_gaps": [
            "Some required technologies not mentioned in resume",
            "Consider adding domain-specific experience",
        ],
        "cover_letter_tips": [
            "Highlight your most relevant projects",
            "Address the company's specific pain points",
        ],
        "interview_prep_topics": [
            "System design fundamentals",
            "Domain-specific technical questions",
            "Behavioral questions using STAR method",
        ],
        "should_apply": should_apply,
        "confidence_level": "High" if match_score >= 70 else "Medium" if match_score >= 50 else "Low",
        "ai_powered": False,
    }


def _mock_chat_response(user_message: str) -> str:
    """Mock chat response for when API key is not available."""
    message_lower = user_message.lower()

    if any(word in message_lower for word in ["summary", "objective"]):
        return "A strong professional summary should be 2-3 sentences highlighting your key skills, years of experience, and what makes you unique. Start with your job title/role, then mention your top 2-3 skills, and end with your career goal or value proposition."

    if any(word in message_lower for word in ["skill", "technology", "tool"]):
        return "For skills sections, I recommend organizing them into categories: Programming Languages, Frameworks, Databases, Cloud/DevOps, and Tools. This makes it easy for both ATS systems and human recruiters to quickly identify your technical proficiency."

    if any(word in message_lower for word in ["experience", "job", "work"]):
        return "For work experience entries, use the PAR format: Problem-Action-Result. Describe a challenge you faced, the action you took, and the quantifiable result. For example: 'Reduced API response time by 45% by implementing Redis caching, improving user experience for 10K+ daily users.'"

    return "I'm your AI resume coach! I can help you improve any section of your resume, suggest better ways to phrase your experience, help you tailor your resume for specific jobs, or answer any career-related questions. What would you like to work on? (Note: Connect a Gemini API key for personalized AI-powered responses!)"
