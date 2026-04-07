"""
pages/3_📊_Analytics.py
Analytics page with Plotly charts: skills distribution, radar chart, keyword cloud.
"""

import streamlit as st
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.skill_analyzer import categorize_skills, get_skill_strength
from utils.keyword_extractor import extract_keywords, extract_bigrams

st.set_page_config(
    page_title="Analytics | AI Resume Analyzer",
    page_icon="📊",
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
            📊 Analytics Dashboard
        </h1>
        <p style='color: #64748B; margin-top: 0.25rem;'>
            Visual breakdown of your resume's strengths and skill distribution.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.get("last_analysis"):
    st.warning("⚠️ No resume analyzed yet. Please upload your resume on the Resume Analysis page first.")
    if st.button("📄 Go to Resume Analysis"):
        st.switch_page("pages/1_📄_Resume_Analysis.py")
    st.stop()

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly not installed. Run `pip install plotly` for charts.")

analysis = st.session_state["last_analysis"]
ats_result = analysis["ats_result"]
skills = analysis["skills"]
stats = analysis["stats"]
resume_text = analysis["parsed"]["text"]

# ---- Top Metrics ----
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 ATS Score", f"{ats_result['total_score']}/100", delta=f"Grade: {ats_result['grade']}")
with col2:
    st.metric("🛠️ Skills Found", len(skills))
with col3:
    st.metric("📚 Sections", stats["section_count"])
with col4:
    skill_strength = get_skill_strength(skills)
    st.metric("💪 Skill Strength", f"{skill_strength['overall_strength']}%")

st.markdown("<br>", unsafe_allow_html=True)

if PLOTLY_AVAILABLE:
    # Chart config
    chart_config = {
        "displayModeBar": False,
        "responsive": True,
    }
    chart_layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8", family="Inter"),
        margin=dict(l=10, r=10, t=30, b=10),
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 ATS Categories",
        "🛠️ Skills Map",
        "☁️ Keywords",
        "📈 Score Analysis",
    ])

    with tab1:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            # Bar chart — Category scores
            cat_scores = ats_result["category_scores"]
            categories = list(cat_scores.keys())
            scores = [v["score"] for v in cat_scores.values()]
            max_scores = [v["max"] for v in cat_scores.values()]
            percentages = [round(s / m * 100) for s, m in zip(scores, max_scores)]

            colors = ["#10B981" if p >= 80 else "#FBBF24" if p >= 50 else "#EF4444" for p in percentages]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=categories,
                x=percentages,
                orientation="h",
                marker=dict(
                    color=colors,
                    line=dict(width=0),
                ),
                text=[f"{p}%" for p in percentages],
                textposition="inside",
                textfont=dict(color="white", size=11, family="Inter"),
                hovertemplate="<b>%{y}</b><br>Score: %{x}%<extra></extra>",
            ))
            fig.update_layout(
                **chart_layout,
                title=dict(text="ATS Category Scores", font=dict(color="var(--text-primary)", size=14)),
                xaxis=dict(range=[0, 105], showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=11)),
                height=350,
                bargap=0.3,
            )
            st.plotly_chart(fig, use_container_width=True, config=chart_config)

        with col_c2:
            # Donut chart — score breakdown
            fig2 = go.Figure(go.Pie(
                values=percentages,
                labels=[c.split()[0] for c in categories],
                hole=0.55,
                marker=dict(colors=[
                    "#7C3AED", "#9F67FA", "var(--text-primary)", "#6D28D9",
                    "#8B5CF6", "#A78BFA", "#DDD6FE", "#EDE9FE",
                ]),
                textfont=dict(color="white", family="Inter"),
                hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
            ))
            fig2.update_layout(
                **chart_layout,
                title=dict(text="Score Distribution", font=dict(color="var(--text-primary)", size=14)),
                showlegend=True,
                legend=dict(font=dict(size=10, color="#94A3B8")),
                height=350,
                annotations=[dict(
                    text=f"<b style='color:white'>{ats_result['total_score']}</b><br><span style='color:#94A3B8'>ATS</span>",
                    x=0.5, y=0.5,
                    font=dict(size=18, color="white", family="Inter"),
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig2, use_container_width=True, config=chart_config)

    with tab2:
        col_sk1, col_sk2 = st.columns(2)

        with col_sk1:
            # Skills by category — horizontal bar
            categorized = categorize_skills(skills)
            cat_names = list(categorized.keys())
            cat_counts = [len(v) for v in categorized.values()]

            fig3 = go.Figure(go.Bar(
                x=cat_counts,
                y=cat_names,
                orientation="h",
                marker=dict(
                    color=cat_counts,
                    colorscale=[[0, "#3B1B8F"], [0.5, "#7C3AED"], [1, "var(--text-primary)"]],
                    showscale=False,
                ),
                text=cat_counts,
                textposition="outside",
                textfont=dict(color="#94A3B8"),
                hovertemplate="<b>%{y}</b><br>%{x} skills<extra></extra>",
            ))
            fig3.update_layout(
                **chart_layout,
                title=dict(text="Skills by Category", font=dict(color="var(--text-primary)", size=14)),
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False),
                height=350,
                bargap=0.3,
            )
            st.plotly_chart(fig3, use_container_width=True, config=chart_config)

        with col_sk2:
            # Radar chart — skill profile
            categories_radar = [
                "Programming", "Frameworks", "Databases",
                "Cloud/DevOps", "Data/AI", "Frontend",
            ]
            cat_map = {
                "Programming Languages": "Programming",
                "Web Frameworks": "Frameworks",
                "Databases": "Databases",
                "Cloud & DevOps": "Cloud/DevOps",
                "Data & AI/ML": "Data/AI",
                "Frontend & Design": "Frontend",
            }
            values_radar = []
            for cat in cat_map:
                count = len(categorized.get(cat, []))
                values_radar.append(min(count * 15, 100))  # Normalize to 100

            values_radar.append(values_radar[0])  # Close polygon
            categories_radar.append(categories_radar[0])

            fig4 = go.Figure()
            fig4.add_trace(go.Scatterpolar(
                r=values_radar,
                theta=categories_radar,
                fill="toself",
                fillcolor="rgba(124, 58, 237, 0.2)",
                line=dict(color="#7C3AED", width=2),
                marker=dict(color="#7C3AED", size=6),
                name="Your Skills",
            ))
            fig4.update_layout(
                **chart_layout,
                title=dict(text="Skill Profile Radar", font=dict(color="var(--text-primary)", size=14)),
                polar=dict(
                    bgcolor="rgba(26,26,46,0.5)",
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=9, color="#64748B"),
                        gridcolor="rgba(124,58,237,0.2)",
                        linecolor="rgba(124,58,237,0.2)",
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=10, color="#94A3B8"),
                        gridcolor="rgba(124,58,237,0.2)",
                        linecolor="rgba(124,58,237,0.2)",
                    ),
                ),
                height=350,
            )
            st.plotly_chart(fig4, use_container_width=True, config=chart_config)

        # All skills list
        st.markdown("**📋 All Detected Skills**")
        for cat, cat_skills in categorized.items():
            if cat_skills:
                tags = " ".join(f'<span class="skill-tag">{s}</span>' for s in cat_skills)
                st.markdown(f"**{cat}:** " + f'<span class="skill-tags">{tags}</span>', unsafe_allow_html=True)

    with tab3:
        # Keyword frequency
        keywords = extract_keywords(resume_text, top_n=20)
        bigrams = extract_bigrams(resume_text, top_n=10)

        col_kw1, col_kw2 = st.columns(2)

        with col_kw1:
            # Top keywords bar chart
            if keywords:
                kw_words = [k[0] for k in keywords[:15]]
                kw_freqs = [k[1] for k in keywords[:15]]

                fig5 = go.Figure(go.Bar(
                    x=kw_freqs,
                    y=kw_words,
                    orientation="h",
                    marker=dict(
                        color=kw_freqs,
                        colorscale=[[0, "#3B1B8F"], [1, "var(--text-primary)"]],
                        showscale=False,
                    ),
                    text=kw_freqs,
                    textposition="outside",
                    textfont=dict(color="#94A3B8"),
                    hovertemplate="<b>%{y}</b><br>Frequency: %{x}<extra></extra>",
                ))
                fig5.update_layout(
                    **chart_layout,
                    title=dict(text="Top Keywords (Frequency)", font=dict(color="var(--text-primary)", size=14)),
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=False, autorange="reversed"),
                    height=400,
                    bargap=0.25,
                )
                st.plotly_chart(fig5, use_container_width=True, config=chart_config)

        with col_kw2:
            # Bigrams
            if bigrams:
                bg_phrases = [b[0] for b in bigrams[:10]]
                bg_freqs = [b[1] for b in bigrams[:10]]

                fig6 = go.Figure(go.Bar(
                    x=bg_freqs,
                    y=bg_phrases,
                    orientation="h",
                    marker=dict(color="#9F67FA"),
                    text=bg_freqs,
                    textposition="outside",
                    textfont=dict(color="#94A3B8"),
                    hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
                ))
                fig6.update_layout(
                    **chart_layout,
                    title=dict(text="Top Keyword Phrases", font=dict(color="var(--text-primary)", size=14)),
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=False, autorange="reversed"),
                    height=400,
                    bargap=0.25,
                )
                st.plotly_chart(fig6, use_container_width=True, config=chart_config)

    with tab4:
        # Score Analysis — gauges for each category
        cat_scores = ats_result["category_scores"]

        col_g1, col_g2 = st.columns(2)
        items = list(cat_scores.items())

        for i, (cat, data) in enumerate(items):
            col = col_g1 if i % 2 == 0 else col_g2
            s = data["score"]
            m = data["max"]
            pct = round(s / m * 100) if m > 0 else 0
            color = "#10B981" if pct >= 80 else "#FBBF24" if pct >= 50 else "#EF4444"

            with col:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=pct,
                    title=dict(text=cat, font=dict(size=12, color="#94A3B8")),
                    number=dict(suffix="%", font=dict(color=color, size=20)),
                    gauge=dict(
                        axis=dict(range=[0, 100], tickwidth=1, tickcolor="gray"),
                        bar=dict(color=color, thickness=0.7),
                        bgcolor="rgba(26,26,46,0.5)",
                        borderwidth=0,
                        steps=[
                            dict(range=[0, 50], color="rgba(239,68,68,0.1)"),
                            dict(range=[50, 80], color="rgba(251,191,36,0.1)"),
                            dict(range=[80, 100], color="rgba(16,185,129,0.1)"),
                        ],
                    ),
                ))
                gauge_layout = {**chart_layout, "height": 170}
                gauge_layout["margin"] = dict(l=20, r=20, t=30, b=10)
                fig_gauge.update_layout(**gauge_layout)
                st.plotly_chart(fig_gauge, use_container_width=True, config=chart_config)

else:
    # Fallback without plotly
    st.markdown("### 📊 ATS Category Scores")
    for cat, data in ats_result["category_scores"].items():
        pct = round(data["score"] / data["max"] * 100) if data["max"] > 0 else 0
        st.progress(pct / 100, text=f"{cat}: {pct}%")

    st.markdown("### 🛠️ Skills")
    if skills:
        st.write(", ".join(skills))
