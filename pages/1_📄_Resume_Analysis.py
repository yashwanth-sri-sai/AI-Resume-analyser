"""
pages/1_📄_Resume_Analysis.py
Core resume analysis page with ATS scoring, AI feedback, and PDF download.
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.file_parser import parse_resume_file, validate_file
from utils.text_processor import get_resume_summary_stats, extract_skills_from_text
from utils.ats_scorer import calculate_ats_score
from utils.llm_client import analyze_resume_with_ai
from utils.report_generator import generate_pdf_report
from utils.db_manager import save_analysis

# ---- Page Config ----
st.set_page_config(
    page_title="Resume Analysis | AI Resume Analyzer",
    page_icon="📄",
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


# ---- Load CSS ----
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---- Header ----
st.markdown(
    """
    <div style='margin-bottom: 1.5rem;'>
        <h1 style='font-size: 2rem; font-weight: 800; color: var(--text-primary); margin: 0;'>
            📄 Resume Analysis
        </h1>
        <p style='color: #64748B; margin-top: 0.25rem;'>
            Upload your resume to get an instant ATS score and AI-powered feedback.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Upload Section ----
col_upload, col_info = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "📤 Upload Your Resume",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX, TXT (max 10MB)",
        label_visibility="visible",
    )

with col_info:
    st.markdown(
        """
        <div style='background: rgba(26,26,46,0.8); border: 1px solid rgba(124,58,237,0.2);
                    border-radius: 12px; padding: 1.25rem; height: 100%;'>
            <div style='font-weight: 600; color: var(--text-primary); margin-bottom: 0.75rem;'>💡 Tips for best results</div>
            <ul style='color: #94A3B8; font-size: 0.85rem; line-height: 1.8; margin: 0; padding-left: 1.2rem;'>
                <li>Use PDF or DOCX format</li>
                <li>Ensure text is selectable (not image-based)</li>
                <li>Include all major sections</li>
                <li>Max file size: 10MB</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---- Analysis ----
if uploaded_file is not None:
    # Validate file
    is_valid, validation_msg = validate_file(uploaded_file)
    if not is_valid:
        st.error(f"❌ {validation_msg}")
        st.stop()

    with st.spinner("🔍 Analyzing your resume..."):
        try:
            # Parse resume
            parsed = parse_resume_file(uploaded_file)
            resume_text = parsed["text"]

            # Get stats
            stats = get_resume_summary_stats(resume_text)

            # Extract skills
            skills = extract_skills_from_text(resume_text)

            # ATS Score
            ats_result = calculate_ats_score(stats, skills)

            # AI Analysis
            ai_analysis = analyze_resume_with_ai(
                resume_text,
                ats_result["total_score"],
                skills,
            )

            # Store in session
            st.session_state["last_analysis"] = {
                "parsed": parsed,
                "stats": stats,
                "skills": skills,
                "ats_result": ats_result,
                "ai_analysis": ai_analysis,
            }

            # Save to DB (if logged in)
            user_id = st.session_state.get("user_id")
            save_analysis(
                file_name=parsed["file_name"],
                file_type=parsed["file_type"],
                ats_score=ats_result["total_score"],
                grade=ats_result["grade"],
                word_count=stats["word_count"],
                skills_found=skills,
                sections_found=stats["sections_found"],
                feedback=ats_result["feedback"],
                resume_text=resume_text,
                user_id=user_id,
            )

        except Exception as e:
            st.error(f"❌ Error processing resume: {str(e)}")
            st.stop()

    st.success("✅ Analysis complete!")
    st.divider()

    # ---- Results ----
    analysis = st.session_state["last_analysis"]
    ats_result = analysis["ats_result"]
    ai_analysis = analysis["ai_analysis"]
    stats = analysis["stats"]
    skills = analysis["skills"]
    parsed = analysis["parsed"]

    # Score Overview
    score = ats_result["total_score"]
    grade = ats_result["grade"]
    grade_label = ats_result["grade_label"]
    grade_color = ats_result["grade_color"]

    col_score, col_metrics = st.columns([1, 2])

    with col_score:
        # Circular score display
        score_pct = score / 100
        circumference = 2 * 3.14159 * 60
        offset = circumference * (1 - score_pct)

        st.markdown(
            f"""
            <div style='text-align: center; padding: 1.5rem; background: rgba(26,26,46,0.8);
                        border: 1px solid rgba(124,58,237,0.2); border-radius: 20px;'>
                <div style='font-size: 0.9rem; color: #64748B; margin-bottom: 1rem; font-weight: 600;
                            text-transform: uppercase; letter-spacing: 0.1em;'>ATS Score</div>
                <svg width="160" height="160" viewBox="0 0 160 160">
                    <circle cx="80" cy="80" r="65" fill="none" stroke="#1A1A2E" stroke-width="14"/>
                    <circle cx="80" cy="80" r="65" fill="none" stroke="{grade_color}" stroke-width="14"
                            stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
                            stroke-linecap="round" transform="rotate(-90 80 80)"
                            style="transition: stroke-dashoffset 1.5s ease;"/>
                    <text x="80" y="72" text-anchor="middle" fill="{grade_color}"
                          font-size="32" font-weight="bold" font-family="Inter, sans-serif">{score}</text>
                    <text x="80" y="90" text-anchor="middle" fill="#94A3B8"
                          font-size="12" font-family="Inter, sans-serif">/100</text>
                </svg>
                <div style='margin-top: 0.5rem;'>
                    <span style='font-size: 2rem; font-weight: 800; color: {grade_color};'>{grade}</span>
                    <div style='color: #94A3B8; font-size: 0.9rem; margin-top: 0.25rem;'>{grade_label}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_metrics:
        # Key metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("📝 Words", stats["word_count"])
            st.metric("📚 Sections", stats["section_count"])
        with m2:
            st.metric("🛠️ Skills Found", len(skills))
            st.metric("⚡ Action Verbs", stats["action_verb_count"])
        with m3:
            st.metric("📊 Quantifications", stats["quantification_count"])
            exp = stats.get("estimated_experience_years", 0)
            st.metric("📅 Exp. Years", f"~{exp}" if exp > 0 else "N/A")

        # Contact info badges
        contact = stats.get("contact_info", {})
        badges = []
        if contact.get("email"):
            badges.append(("✅", "Email"))
        if contact.get("phone"):
            badges.append(("✅", "Phone"))
        if contact.get("linkedin"):
            badges.append(("✅", "LinkedIn"))
        if contact.get("github"):
            badges.append(("✅", "GitHub"))

        if badges:
            badge_html = " ".join(
                f'<span style="background: rgba(16,185,129,0.15); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.3); border-radius: 20px; padding: 0.2rem 0.75rem; font-size: 0.8rem;">{icon} {label}</span>'
                for icon, label in badges
            )
            st.markdown(f"<div style='margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.4rem;'>{badge_html}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Tabs ----
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Category Breakdown",
        "🛠️ Skills",
        "🤖 AI Analysis",
        "📝 Raw Text",
    ])

    with tab1:
        st.markdown("### ATS Category Scores")
        cat_scores = ats_result["category_scores"]

        for cat, data in cat_scores.items():
            s = data["score"]
            m = data["max"]
            pct = int((s / m) * 100) if m > 0 else 0
            color = "#10B981" if pct >= 80 else "#FBBF24" if pct >= 50 else "#EF4444"

            st.markdown(
                f"""
                <div class="progress-wrapper">
                    <div class="progress-label">
                        <span style='color: var(--text-primary); font-weight: 500;'>{cat}</span>
                        <span style='color: {color}; font-weight: 700;'>{s}/{m}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style='width: {pct}%; background: linear-gradient(90deg, {color}80, {color});'></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Feedback")

        positives = ats_result.get("positives", [])
        improvements = ats_result.get("improvements", [])

        if positives:
            st.markdown("**✅ Strengths**")
            for item in positives:
                st.markdown(
                    f'<div class="feedback-card feedback-positive">{item}</div>',
                    unsafe_allow_html=True,
                )

        if improvements:
            st.markdown("**⚠️ Areas to Improve**")
            for item in improvements:
                emoji = item[0] if item else "•"
                css_class = "feedback-negative" if item.startswith("❌") else "feedback-warning"
                st.markdown(
                    f'<div class="feedback-card {css_class}">{item}</div>',
                    unsafe_allow_html=True,
                )

    with tab2:
        st.markdown("### 🛠️ Detected Skills")
        if skills:
            from utils.skill_analyzer import categorize_skills
            categorized = categorize_skills(skills)

            for cat, cat_skills in categorized.items():
                if cat_skills:
                    st.markdown(f"**{cat}**")
                    tags = " ".join(
                        f'<span class="skill-tag">{s}</span>' for s in cat_skills
                    )
                    st.markdown(
                        f'<div class="skill-tags">{tags}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown("")
        else:
            st.warning("No specific technical skills detected in your resume.")

    with tab3:
        st.markdown("### 🤖 AI-Powered Analysis")

        if not ai_analysis.get("ai_powered", False):
            st.info(
                "💡 **Demo Mode** — Add your Gemini API key in the sidebar settings for personalized AI analysis.",
                icon="ℹ️",
            )

        col_ai1, col_ai2 = st.columns(2)
        with col_ai1:
            if ai_analysis.get("overall_assessment"):
                st.markdown("**📝 Overall Assessment**")
                st.markdown(
                    f"""
                    <div style='background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.3);
                                border-radius: 12px; padding: 1rem; color: var(--text-primary); font-size: 0.9rem; line-height: 1.6;'>
                        {ai_analysis['overall_assessment']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if ai_analysis.get("career_level"):
                st.metric("🎯 Career Level", ai_analysis["career_level"])

            if ai_analysis.get("suggested_roles"):
                st.markdown("**💼 Suggested Job Roles**")
                for role in ai_analysis["suggested_roles"]:
                    st.markdown(
                        f'<div style="background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.2); border-radius: 8px; padding: 0.5rem 1rem; margin-bottom: 0.5rem; color: var(--text-primary); font-size: 0.875rem;">💼 {role}</div>',
                        unsafe_allow_html=True,
                    )

        with col_ai2:
            if ai_analysis.get("strengths"):
                st.markdown("**✅ Key Strengths**")
                for s in ai_analysis["strengths"]:
                    st.markdown(
                        f'<div class="feedback-card feedback-positive">✅ {s}</div>',
                        unsafe_allow_html=True,
                    )

            if ai_analysis.get("improvements"):
                st.markdown("**⚠️ Key Improvements**")
                for imp in ai_analysis["improvements"]:
                    st.markdown(
                        f'<div class="feedback-card feedback-warning">⚠️ {imp}</div>',
                        unsafe_allow_html=True,
                    )

        if ai_analysis.get("summary_rewrite"):
            st.markdown("**✍️ Suggested Summary Rewrite**")
            st.markdown(
                f"""
                <div style='background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3);
                            border-radius: 12px; padding: 1rem; color: #D1FAE5; font-size: 0.9rem; line-height: 1.6;
                            font-style: italic;'>
                    "{ai_analysis['summary_rewrite']}"
                </div>
                """,
                unsafe_allow_html=True,
            )

        if ai_analysis.get("rewrite_tips"):
            st.markdown("**💡 Rewrite Tips**")
            for tip in ai_analysis["rewrite_tips"]:
                st.markdown(
                    f'<div class="feedback-card feedback-tip">💡 {tip}</div>',
                    unsafe_allow_html=True,
                )

    with tab4:
        st.markdown("### 📝 Extracted Resume Text")
        st.text_area(
            "Resume Content",
            value=resume_text,
            height=400,
            disabled=True,
            label_visibility="collapsed",
        )

    st.divider()

    # ---- Download Report ----
    st.markdown("### 📥 Download Report")
    col_dl1, col_dl2, col_dl3 = st.columns(3)

    with col_dl1:
        report_bytes = generate_pdf_report(
            file_name=parsed["file_name"],
            resume_text=resume_text,
            ats_result=ats_result,
            skills=skills,
            contact_info=stats.get("contact_info", {}),
            ai_analysis=ai_analysis,
        )

        is_pdf = report_bytes[:4] == b"%PDF"
        file_ext = "pdf" if is_pdf else "txt"
        mime_type = "application/pdf" if is_pdf else "text/plain"

        st.download_button(
            label="📄 Download Full Report",
            data=report_bytes,
            file_name=f"resume_analysis_{parsed['file_name'].replace('.', '_')}.{file_ext}",
            mime=mime_type,
            use_container_width=True,
        )

    with col_dl2:
        # JSON export
        import json
        export_data = {
            "file_name": parsed["file_name"],
            "ats_score": ats_result["total_score"],
            "grade": ats_result["grade"],
            "skills": skills,
            "sections_found": stats["sections_found"],
            "feedback": ats_result["feedback"],
        }
        st.download_button(
            label="📊 Export JSON Data",
            data=json.dumps(export_data, indent=2),
            file_name="resume_analysis.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_dl3:
        if st.button("💬 Chat About This Resume", use_container_width=True):
            st.switch_page("pages/4_💬_AI_Chat.py")

elif st.session_state.get("last_analysis"):
    # Show previous analysis
    st.info("📂 Showing your last analysis. Upload a new resume to analyze again.")
    analysis = st.session_state["last_analysis"]
    score = analysis["ats_result"]["total_score"]
    grade = analysis["ats_result"]["grade"]
    st.markdown(f"**Last analyzed:** {analysis['parsed']['file_name']} | **Score:** {score}/100 | **Grade:** {grade}")
else:
    # Empty state
    st.markdown(
        """
        <div style='text-align: center; padding: 4rem 2rem; background: rgba(26,26,46,0.5);
                    border: 2px dashed rgba(124,58,237,0.3); border-radius: 20px; margin-top: 1rem;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>📄</div>
            <div style='font-size: 1.2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;'>
                No resume uploaded yet
            </div>
            <div style='color: #64748B; font-size: 0.9rem;'>
                Upload a PDF, DOCX, or TXT file above to get started
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
