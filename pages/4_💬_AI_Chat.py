"""
pages/4_💬_AI_Chat.py
AI Chat interface — ask questions about your resume, get career coaching.
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.llm_client import chat_with_resume

st.set_page_config(
    page_title="AI Chat Coach | AI Resume Analyzer",
    page_icon="💬",
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
            💬 AI Career Coach
        </h1>
        <p style='color: #64748B; margin-top: 0.25rem;'>
            Ask anything about your resume. Get personalized advice from your AI coach.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Check resume ----
resume_loaded = st.session_state.get("last_analysis") is not None
resume_text = ""

if resume_loaded:
    analysis = st.session_state["last_analysis"]
    resume_text = analysis["parsed"]["text"]
    file_name = analysis["parsed"]["file_name"]

    st.markdown(
        f"""
        <div style='background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3);
                    border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 1rem;
                    display: flex; align-items: center; gap: 0.5rem;'>
            <span>✅</span>
            <span style='color: #6EE7B7; font-size: 0.9rem;'>Resume loaded: <b>{file_name}</b> — The AI coach has context about your resume.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("💡 No resume loaded yet. The coach will still help, but upload a resume for personalized advice!")
    col_nav, _ = st.columns([1, 3])
    with col_nav:
        if st.button("📄 Upload Resume First"):
            st.switch_page("pages/1_📄_Resume_Analysis.py")

# ---- Initialize chat ----
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ---- Suggested Questions ----
st.markdown("**💡 Suggested Questions:**")
suggested = [
    "How can I improve my resume summary?",
    "What skills should I add for a software engineering role?",
    "How do I quantify my achievements?",
    "Review my work experience section",
    "What's a good ATS score to aim for?",
    "Help me prepare for technical interviews",
]

cols_sug = st.columns(3)
for i, q in enumerate(suggested):
    with cols_sug[i % 3]:
        if st.button(q, key=f"sug_{i}", use_container_width=True):
            st.session_state["pending_q"] = q
            st.rerun()

st.markdown("---")

# ---- Chat Display ----
chat_container = st.container()
with chat_container:
    if not st.session_state["chat_history"]:
        st.markdown(
            """
            <div style='text-align: center; padding: 3rem 2rem; opacity: 0.7;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>🤖</div>
                <div style='font-size: 1.1rem; font-weight: 600; color: var(--text-primary);'>
                    Hi! I'm your AI Career Coach
                </div>
                <div style='color: #64748B; margin-top: 0.5rem; font-size: 0.9rem;'>
                    Ask me anything about your resume, job search, or career growth.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: flex-end; margin-bottom: 1rem;'>
                        <div class="chat-message-user">
                            {msg['content']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                ai_icon = "🤖" if os.getenv("GEMINI_API_KEY") else "🔵"
                st.markdown(
                    f"""
                    <div style='display: flex; gap: 0.75rem; margin-bottom: 1rem;'>
                        <div style='font-size: 1.5rem; flex-shrink: 0; margin-top: 0.25rem;'>{ai_icon}</div>
                        <div class="chat-message-ai">
                            {msg['content'].replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ---- Handle pending question from suggestions ----
pending = st.session_state.pop("pending_q", None)

# ---- Input ----
col_input, col_send = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        "Your message",
        value=pending or "",
        placeholder="Ask about your resume, skills, career advice...",
        label_visibility="collapsed",
        key="chat_input",
    )
with col_send:
    send_clicked = st.button("Send 🚀", use_container_width=True, type="primary")

if (send_clicked or pending) and user_input:
    # Add user message
    st.session_state["chat_history"].append({
        "role": "user",
        "content": user_input,
    })

    # Get AI response
    with st.spinner("🤖 Thinking..."):
        ai_response = chat_with_resume(
            resume_text=resume_text,
            conversation_history=st.session_state["chat_history"][:-1],
            user_message=user_input,
        )

    # Add AI response
    st.session_state["chat_history"].append({
        "role": "assistant",
        "content": ai_response,
    })

    st.rerun()

# ---- Sidebar Controls ----
with st.sidebar:
    st.markdown("### 💬 Chat Controls")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()

    if st.session_state["chat_history"]:
        # Export chat
        chat_export = "\n\n".join(
            f"{'You' if m['role'] == 'user' else 'AI Coach'}: {m['content']}"
            for m in st.session_state["chat_history"]
        )
        st.download_button(
            "📥 Export Chat",
            data=chat_export,
            file_name="career_coaching_chat.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.divider()
    st.markdown("### 🤖 AI Status")
    if os.getenv("GEMINI_API_KEY"):
        st.success("✅ Gemini AI Active")
    else:
        st.warning("⚠️ Demo Mode")
        st.caption("Add your Gemini API key in Settings for real AI responses.")

    st.markdown("### 📝 Quick Tips")
    st.markdown(
        """
        <div style='color: #64748B; font-size: 0.8rem; line-height: 1.8;'>
            • Be specific in your questions<br>
            • Mention the job role you're targeting<br>
            • Ask for rewrites of specific sections<br>
            • Request interview prep tips
        </div>
        """,
        unsafe_allow_html=True,
    )
