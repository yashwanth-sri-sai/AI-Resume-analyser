"""
pages/6_📁_History.py
Analysis history: view past analyses, download reports, track score trends.
"""

import streamlit as st
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db_manager import get_user_analyses, get_analysis_by_id
from utils.auth import is_logged_in, get_current_user
from utils.report_generator import generate_pdf_report

st.set_page_config(
    page_title="History | AI Resume Analyzer",
    page_icon="📁",
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
            📁 Analysis History
        </h1>
        <p style='color: #64748B; margin-top: 0.25rem;'>
            Review your past analyses and track your resume improvement journey.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not is_logged_in():
    st.warning("⚠️ Please log in to view your analysis history.")
    col_nav, _ = st.columns([1, 3])
    with col_nav:
        if st.button("🔐 Log In / Register"):
            st.switch_page("pages/5_🔐_Authentication.py")

    # Show current session analysis if available
    if st.session_state.get("last_analysis"):
        st.markdown("---")
        st.info("Showing your current session analysis (not saved to account):")
        analysis = st.session_state["last_analysis"]
        ats = analysis["ats_result"]
        parsed = analysis["parsed"]

        st.markdown(
            f"""
            <div style='background: rgba(26,26,46,0.8); border: 1px solid rgba(124,58,237,0.2);
                        border-radius: 12px; padding: 1.25rem;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <div style='font-weight: 700; color: var(--text-primary);'>📄 {parsed['file_name']}</div>
                        <div style='color: #64748B; font-size: 0.8rem; margin-top: 0.25rem;'>Current session</div>
                    </div>
                    <div style='text-align: right;'>
                        <div style='font-size: 1.5rem; font-weight: 800; color: {ats['grade_color']};'>
                            {ats['total_score']}/100
                        </div>
                        <div style='color: #64748B; font-size: 0.8rem;'>Grade: {ats['grade']}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.stop()

user = get_current_user()
analyses = get_user_analyses(user["id"])

if not analyses:
    st.markdown(
        """
        <div style='text-align: center; padding: 4rem 2rem; background: rgba(26,26,46,0.5);
                    border: 2px dashed rgba(124,58,237,0.3); border-radius: 20px;'>
            <div style='font-size: 4rem;'>📭</div>
            <div style='font-size: 1.2rem; font-weight: 700; color: var(--text-primary); margin: 1rem 0 0.5rem;'>
                No analyses yet
            </div>
            <div style='color: #64748B;'>Upload your resume to get your first analysis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("📄 Analyze My Resume", type="primary"):
        st.switch_page("pages/1_📄_Resume_Analysis.py")
    st.stop()

# ---- Stats Summary ----
scores = [a["ats_score"] for a in analyses if a["ats_score"]]
avg_score = round(sum(scores) / len(scores)) if scores else 0
best_score = max(scores) if scores else 0
latest_score = scores[0] if scores else 0

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.metric("📊 Total Analyses", len(analyses))
with col_s2:
    st.metric("🎯 Latest Score", f"{latest_score}/100")
with col_s3:
    st.metric("⭐ Best Score", f"{best_score}/100")
with col_s4:
    st.metric("📈 Average Score", f"{avg_score}/100")

st.markdown("<br>", unsafe_allow_html=True)

# ---- Score Trend Chart ----
if len(analyses) > 1:
    try:
        import plotly.graph_objects as go

        dates = [a["created_at"] for a in reversed(analyses)]
        score_values = [a["ats_score"] for a in reversed(analyses)]
        file_names = [a["file_name"][:20] for a in reversed(analyses)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=score_values,
            mode="lines+markers+text",
            line=dict(color="#7C3AED", width=2.5),
            marker=dict(color="var(--text-primary)", size=8, line=dict(color="#7C3AED", width=2)),
            text=[f"{s}/100" for s in score_values],
            textposition="top center",
            textfont=dict(color="#94A3B8", size=10),
            hovertemplate="<b>%{x}</b><br>Score: %{y}/100<extra></extra>",
            fill="tozeroy",
            fillcolor="rgba(124, 58, 237, 0.1)",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94A3B8", family="Inter"),
            title=dict(text="📈 ATS Score Trend", font=dict(color="var(--text-primary)", size=14)),
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(124,58,237,0.1)",
                range=[0, 105],
                ticksuffix="/100",
                tickfont=dict(size=10),
            ),
            height=250,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except ImportError:
        pass

# ---- History Table ----
st.markdown("### 📋 All Analyses")

for i, analysis in enumerate(analyses):
    score = analysis["ats_score"] or 0
    grade = analysis.get("grade", "N/A")
    color = "#10B981" if score >= 80 else "#FBBF24" if score >= 60 else "#EF4444"
    skills = analysis.get("skills_found", [])
    sections = analysis.get("sections_found", [])

    with st.expander(
        f"📄 {analysis['file_name']} — {score}/100 ({grade}) · {analysis['created_at']}",
        expanded=(i == 0),
    ):
        col_det1, col_det2 = st.columns(2)
        with col_det1:
            st.markdown(f"**📅 Date:** {analysis['created_at']}")
            st.markdown(f"**📝 Words:** {analysis['word_count']}")
            st.markdown(f"**🛠️ Skills Found:** {len(skills)}")
            st.markdown(f"**📚 Sections:** {', '.join(sections)}" if sections else "**Sections:** N/A")

        with col_det2:
            st.markdown(
                f"""
                <div style='text-align: center; background: rgba(26,26,46,0.8);
                            border: 1px solid rgba(124,58,237,0.2); border-radius: 12px; padding: 1.25rem;'>
                    <div style='font-size: 2.5rem; font-weight: 800; color: {color};'>{score}/100</div>
                    <div style='font-size: 1.2rem; font-weight: 700; color: {color};'>Grade: {grade}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if skills:
            st.markdown("**Skills:**")
            tags = " ".join(f'<span class="skill-tag">{s}</span>' for s in skills[:15])
            st.markdown(f'<div class="skill-tags">{tags}</div>', unsafe_allow_html=True)

        # Download button for this analysis
        col_dl1, col_dl2, _ = st.columns([1, 1, 2])
        with col_dl1:
            # Get full analysis for PDF generation
            full = get_analysis_by_id(analysis["id"])
            if full:
                mock_ats = {
                    "total_score": full["ats_score"],
                    "grade": full["grade"],
                    "grade_label": "",
                    "grade_color": color,
                    "category_scores": {},
                    "feedback": full["feedback"],
                    "improvements": [f for f in full["feedback"] if f.startswith(("❌", "⚠️"))],
                    "positives": [f for f in full["feedback"] if f.startswith("✅")],
                }
                report = generate_pdf_report(
                    file_name=full["file_name"],
                    resume_text=full["resume_text"] or "",
                    ats_result=mock_ats,
                    skills=full["skills_found"],
                    contact_info={},
                )
                file_ext = "pdf" if report[:4] == b"%PDF" else "txt"
                st.download_button(
                    "📄 Download Report",
                    data=report,
                    file_name=f"analysis_{analysis['id']}.{file_ext}",
                    mime="application/pdf" if file_ext == "pdf" else "text/plain",
                    key=f"dl_{analysis['id']}",
                    use_container_width=True,
                )
