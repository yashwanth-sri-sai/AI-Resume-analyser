"""
pages/2_💼_Job_Matching.py
Job description matching with similarity score, skill gap, and keyword analysis.
"""

import streamlit as st
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.similarity import compute_tfidf_similarity, rank_job_roles
from utils.keyword_extractor import keyword_match_analysis, extract_tech_skills_from_jd
from utils.skill_analyzer import analyze_skill_gap
from utils.llm_client import match_resume_to_job

st.set_page_config(
    page_title="Job Matching | AI Resume Analyzer",
    page_icon="💼",
    layout="wide",
)

# ---- Shared Sidebar Theme Toggle ----
with st.sidebar:
    st.markdown("<div style='font-family: Outfit, sans-serif; font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em; margin: 0.5rem 0 0.75rem;'>🌈 Theme</div>", unsafe_allow_html=True)
    
    # Store theme in session state explicitly so it persists
    if "theme_toggle_val" not in st.session_state:
        st.session_state.theme_toggle_val = False

    def sync_theme():
        st.session_state.theme_toggle_val = st.session_state.theme_toggle

    theme_on = st.toggle("🌙 Dark / ☀️ Light Mode", key="theme_toggle", value=st.session_state.theme_toggle_val, on_change=sync_theme)

    import streamlit.components.v1 as components
    components.html(f"""
        <script>
            const body = window.parent.document.body;
            const container = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
            if ({str(theme_on).lower()}) {{
                body.classList.add('light-theme');
                if(container) container.classList.add('light-theme');
            }} else {{
                body.classList.remove('light-theme');
                if(container) container.classList.remove('light-theme');
            }}
        </script>
    """, height=0, width=0)


# ---- Theme Sync ----
import streamlit.components.v1 as components
theme_on = st.session_state.get("theme_toggle", False)
components.html(f"""
    <script>
        const body = window.parent.document.body;
        const container = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if ({str(theme_on).lower()}) {{
            body.classList.add('light-theme');
            if(container) container.classList.add('light-theme');
        }} else {{
            body.classList.remove('light-theme');
            if(container) container.classList.remove('light-theme');
        }}
    </script>
""", height=0, width=0)


css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <div style='margin-bottom: 1.5rem;'>
        <h1 style='font-size: 2rem; font-weight: 800; color: var(--text-primary); margin: 0;'>
            💼 Job Matching
        </h1>
        <p style='color: #64748B; margin-top: 0.25rem;'>
            Paste a job description to see how well your resume matches.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Check for resume in session ----
if not st.session_state.get("last_analysis"):
    st.warning("⚠️ No resume analyzed yet. Please upload your resume on the **Resume Analysis** page first.")
    if st.button("📄 Go to Resume Analysis"):
        st.switch_page("pages/1_📄_Resume_Analysis.py")
    st.stop()

analysis = st.session_state["last_analysis"]
resume_text = analysis["parsed"]["text"]
resume_skills = analysis["skills"]

# ---- Job Description Input ----
col_input, col_preset = st.columns([3, 1])

with col_input:
    st.markdown("#### 📋 Paste Job Description")
    job_description = st.text_area(
        "Job Description",
        placeholder="Paste the full job description here...\n\nExample:\nWe are looking for a Senior Software Engineer with 5+ years of experience in Python, FastAPI, PostgreSQL, and AWS...",
        height=250,
        label_visibility="collapsed",
    )

with col_preset:
    st.markdown("#### 🎯 Or Try a Preset")
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "job_roles.json")
    job_roles = []
    if os.path.exists(data_path):
        with open(data_path) as f:
            job_roles = json.load(f)

    selected_role = st.selectbox(
        "Choose job role",
        options=["-- Select --"] + [r["title"] for r in job_roles],
        label_visibility="visible",
    )

    if selected_role != "-- Select --":
        role_data = next(r for r in job_roles if r["title"] == selected_role)
        jd_template = (
            f"{role_data['title']}\n\n"
            f"About the Role:\n{role_data['description']}\n\n"
            f"Required Skills:\n" + "\n".join(f"• {s}" for s in role_data["required_skills"]) +
            f"\n\nNice to Have:\n" + "\n".join(f"• {s}" for s in role_data.get("nice_to_have", [])) +
            f"\n\nExperience Level: {role_data.get('experience_level', '')}"
        )
        if st.button("📥 Load This JD", use_container_width=True):
            st.session_state["preset_jd"] = jd_template
            st.rerun()

    if st.session_state.get("preset_jd") and not job_description:
        job_description = st.session_state["preset_jd"]

# ---- Analyze Button ----
if st.button("🔍 Analyze Match", type="primary", use_container_width=False):
    if not job_description or len(job_description.strip()) < 50:
        st.error("Please paste a job description (at least 50 characters).")
    else:
        with st.spinner("🔄 Computing similarity and analyzing match..."):
            # TF-IDF Similarity
            similarity_score = compute_tfidf_similarity(resume_text, job_description)

            # Keyword matching
            keyword_result = keyword_match_analysis(resume_text, job_description)

            # Tech skills in JD
            jd_tech_skills = extract_tech_skills_from_jd(job_description)

            # Skill gap
            skill_gap = analyze_skill_gap(resume_skills, jd_tech_skills) if jd_tech_skills else {
                "matched_skills": [],
                "missing_skills": [],
                "match_percentage": 0,
                "recommendations": [],
            }

            # AI Match Analysis
            ai_match = match_resume_to_job(resume_text, job_description, keyword_result["match_score"])

        st.session_state["job_match"] = {
            "similarity_score": similarity_score,
            "keyword_result": keyword_result,
            "jd_tech_skills": jd_tech_skills,
            "skill_gap": skill_gap,
            "ai_match": ai_match,
            "job_description": job_description,
        }
        st.rerun()

# ---- Results ----
if st.session_state.get("job_match"):
    match_data = st.session_state["job_match"]
    similarity = match_data["similarity_score"]
    keyword_result = match_data["keyword_result"]
    skill_gap = match_data["skill_gap"]
    ai_match = match_data["ai_match"]

    st.divider()

    # ---- Score Overview ----
    overall_score = round((similarity * 0.4 + keyword_result["match_score"] * 0.6))

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        color = "#10B981" if overall_score >= 70 else "#FBBF24" if overall_score >= 50 else "#EF4444"
        st.markdown(
            f"""
            <div style='background: rgba(26,26,46,0.8); border: 1px solid rgba(124,58,237,0.2);
                        border-radius: 16px; padding: 1.5rem; text-align: center;'>
                <div style='font-size: 0.85rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em;'>Overall Match</div>
                <div style='font-size: 3rem; font-weight: 800; color: {color}; line-height: 1.1; margin: 0.5rem 0;'>{overall_score}%</div>
                <div style='color: #94A3B8; font-size: 0.9rem;'>
                    {"🟢 Strong Match" if overall_score >= 70 else "🟡 Moderate Match" if overall_score >= 50 else "🔴 Weak Match"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s2:
        st.markdown(
            f"""
            <div style='background: rgba(26,26,46,0.8); border: 1px solid rgba(124,58,237,0.2);
                        border-radius: 16px; padding: 1.5rem; text-align: center;'>
                <div style='font-size: 0.85rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em;'>Content Similarity</div>
                <div style='font-size: 3rem; font-weight: 800; color: #7C3AED; line-height: 1.1; margin: 0.5rem 0;'>{similarity:.0f}%</div>
                <div style='color: #94A3B8; font-size: 0.9rem;'>TF-IDF Cosine Similarity</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s3:
        kw_pct = keyword_result["match_score"]
        st.markdown(
            f"""
            <div style='background: rgba(26,26,46,0.8); border: 1px solid rgba(124,58,237,0.2);
                        border-radius: 16px; padding: 1.5rem; text-align: center;'>
                <div style='font-size: 0.85rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em;'>Keyword Match</div>
                <div style='font-size: 3rem; font-weight: 800; color: var(--text-primary); line-height: 1.1; margin: 0.5rem 0;'>{kw_pct}%</div>
                <div style='color: #94A3B8; font-size: 0.9rem;'>{keyword_result["total_matched"]}/{keyword_result["total_jd_keywords"]} keywords</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Tabs ----
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 AI Assessment",
        "🔑 Keywords",
        "🛠️ Skill Gap",
        "📈 Suggestions",
    ])

    with tab1:
        if ai_match:
            if not ai_match.get("ai_powered", False):
                st.info("💡 Running in demo mode. Add your Gemini API key for real AI analysis.")

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                if ai_match.get("fit_assessment"):
                    st.markdown("**📋 Fit Assessment**")
                    st.markdown(
                        f"""
                        <div style='background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.3);
                                    border-radius: 12px; padding: 1rem; color: var(--text-primary); font-size: 0.9rem; line-height: 1.6;'>
                            {ai_match['fit_assessment']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                if ai_match.get("should_apply") is not None:
                    should = ai_match["should_apply"]
                    confidence = ai_match.get("confidence_level", "Medium")
                    icon = "✅" if should else "⚠️"
                    msg = "Apply to this job!" if should else "Consider building missing skills first."
                    st.markdown(
                        f"""
                        <div style='background: rgba({"16,185,129" if should else "251,191,36"},0.1);
                                    border: 1px solid rgba({"16,185,129" if should else "251,191,36"},0.3);
                                    border-radius: 12px; padding: 1rem; margin-top: 1rem;'>
                            <div style='font-size: 1.1rem; font-weight: 700; color: {"#6EE7B7" if should else "#FDE68A"};'>
                                {icon} {msg}
                            </div>
                            <div style='color: #94A3B8; font-size: 0.85rem; margin-top: 0.25rem;'>
                                AI Confidence: {confidence}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with col_a2:
                if ai_match.get("top_matching_points"):
                    st.markdown("**✅ What Matches**")
                    for pt in ai_match["top_matching_points"]:
                        st.markdown(
                            f'<div class="feedback-card feedback-positive">✅ {pt}</div>',
                            unsafe_allow_html=True,
                        )

                if ai_match.get("critical_gaps"):
                    st.markdown("**❌ Critical Gaps**")
                    for gap in ai_match["critical_gaps"]:
                        st.markdown(
                            f'<div class="feedback-card feedback-negative">❌ {gap}</div>',
                            unsafe_allow_html=True,
                        )

            if ai_match.get("interview_prep_topics"):
                st.markdown("**🎯 Interview Prep Topics**")
                cols_prep = st.columns(3)
                for i, topic in enumerate(ai_match["interview_prep_topics"]):
                    with cols_prep[i % 3]:
                        st.markdown(
                            f'<div style="background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.2); border-radius: 8px; padding: 0.5rem 0.75rem; margin-bottom: 0.4rem; color: var(--text-primary); font-size: 0.8rem;">📌 {topic}</div>',
                            unsafe_allow_html=True,
                        )

    with tab2:
        col_kw1, col_kw2 = st.columns(2)
        with col_kw1:
            st.markdown("**✅ Matched Keywords**")
            matched = keyword_result.get("matched_keywords", [])
            if matched:
                tags = " ".join(f'<span class="skill-tag skill-tag-matched">{kw}</span>' for kw in matched[:20])
                st.markdown(f'<div class="skill-tags">{tags}</div>', unsafe_allow_html=True)
            else:
                st.caption("No matching keywords found")

        with col_kw2:
            st.markdown("**❌ Missing Keywords**")
            missing = keyword_result.get("missing_keywords", [])
            if missing:
                tags = " ".join(f'<span class="skill-tag skill-tag-missing">{kw}</span>' for kw in missing[:20])
                st.markdown(f'<div class="skill-tags">{tags}</div>', unsafe_allow_html=True)
            else:
                st.success("Great! No critical missing keywords detected.")

    with tab3:
        jd_skills = match_data.get("jd_tech_skills", [])
        if jd_skills:
            col_sg1, col_sg2 = st.columns(2)
            with col_sg1:
                st.markdown("**✅ Skills You Have**")
                matched_skills = skill_gap.get("matched_skills", [])
                if matched_skills:
                    tags = " ".join(f'<span class="skill-tag skill-tag-matched">{s}</span>' for s in matched_skills)
                    st.markdown(f'<div class="skill-tags">{tags}</div>', unsafe_allow_html=True)
                else:
                    st.caption("No matching skills detected")

            with col_sg2:
                st.markdown("**❌ Skills to Learn**")
                missing_skills = skill_gap.get("missing_skills", [])
                if missing_skills:
                    tags = " ".join(f'<span class="skill-tag skill-tag-missing">{s}</span>' for s in missing_skills)
                    st.markdown(f'<div class="skill-tags">{tags}</div>', unsafe_allow_html=True)
                else:
                    st.success("You have all the required technical skills!")

            pct = skill_gap.get("match_percentage", 0)
            st.markdown(
                f"""
                <div style='margin-top: 1rem;'>
                    <div style='display: flex; justify-content: space-between; font-size: 0.85rem;
                                color: #94A3B8; margin-bottom: 0.35rem;'>
                        <span>Skill Match Rate</span>
                        <span style='color: {"#10B981" if pct >= 70 else "#FBBF24" if pct >= 50 else "#EF4444"};
                                     font-weight: 700;'>{pct}%</span>
                    </div>
                    <div class='progress-bar'>
                        <div class='progress-fill' style='width: {pct}%;'></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Learning recommendations
            recommendations = skill_gap.get("recommendations", [])
            if recommendations:
                st.markdown("<br>**📚 Learning Resources**")
                for rec in recommendations:
                    st.markdown(
                        f"""
                        <div style='background: rgba(26,26,46,0.8); border: 1px solid rgba(124,58,237,0.2);
                                    border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
                                    display: flex; justify-content: space-between; align-items: center;'>
                            <div style='color: var(--text-primary); font-weight: 500;'>🛠️ {rec['skill']}</div>
                            <a href='{rec['url']}' target='_blank'
                               style='color: #7C3AED; font-size: 0.8rem; text-decoration: none;
                                      background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.3);
                                      border-radius: 6px; padding: 0.25rem 0.75rem;'>
                                {rec['platform']} →
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No specific technical skills detected in the job description. The keyword analysis tab can still help.")

    with tab4:
        if ai_match.get("cover_letter_tips"):
            st.markdown("**📝 Cover Letter Tips**")
            for tip in ai_match["cover_letter_tips"]:
                st.markdown(
                    f'<div class="feedback-card feedback-tip">💡 {tip}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("**🎯 Next Steps**")
        pct = skill_gap.get("match_percentage", 0)
        score = keyword_result.get("match_score", 0)

        if score >= 70:
            steps = [
                "✅ Your resume is well-matched for this role — apply with confidence!",
                "📝 Tailor your cover letter to highlight the specific tools mentioned in the JD",
                "🎯 Prepare for technical interviews on the topics listed above",
                "🔗 Connect with the company's employees on LinkedIn before applying",
            ]
        elif score >= 50:
            steps = [
                "⚠️ Moderate match — customize your resume before applying",
                "🔑 Add the missing keywords naturally into your experience descriptions",
                "📖 Study the required skills you're missing (see learning resources above)",
                "💼 Highlight transferable skills that relate to the job requirements",
            ]
        else:
            steps = [
                "📚 Focus on learning the key missing skills (2-3 months of study)",
                "🏗️ Build 1-2 portfolio projects using the required technologies",
                "🔄 Start with similar roles that better match your current skill set",
                "📝 Completely rewrite your resume focusing on the most relevant experience",
            ]

        for step in steps:
            st.markdown(
                f'<div class="feedback-card feedback-tip" style="margin-bottom: 0.5rem;">{step}</div>',
                unsafe_allow_html=True,
            )

# ---- Sidebar: Job Roles ----
with st.sidebar:
    st.markdown("### 🏆 Best Matching Roles")
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "job_roles.json")
    if os.path.exists(data_path):
        with open(data_path) as f:
            all_roles = json.load(f)
        ranked = rank_job_roles(resume_text, all_roles)[:5]
        for role in ranked:
            score = role["similarity_score"]
            color = "#10B981" if score >= 50 else "#FBBF24" if score >= 30 else "#EF4444"
            st.markdown(
                f"""
                <div style='background: rgba(26,26,46,0.8); border: 1px solid rgba(124,58,237,0.2);
                            border-radius: 10px; padding: 0.75rem; margin-bottom: 0.5rem;'>
                    <div style='font-weight: 600; color: var(--text-primary); font-size: 0.85rem;'>{role['title']}</div>
                    <div style='font-size: 0.75rem; color: #64748B;'>{role['category']}</div>
                    <div style='font-size: 0.85rem; color: {color}; font-weight: 700; margin-top: 0.25rem;'>
                        {score:.0f}% match
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
