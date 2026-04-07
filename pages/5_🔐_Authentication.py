"""
pages/5_🔐_Authentication.py
User registration, login, and account management.
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.auth import (
    hash_password, verify_password, validate_password_strength,
    validate_email, login_user, logout_user, is_logged_in, get_current_user,
)
from utils.db_manager import create_user, get_user_by_username, get_user_by_email

st.set_page_config(
    page_title="Account | AI Resume Analyzer",
    page_icon="🔐",
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
            🔐 Account
        </h1>
        <p style='color: #64748B; margin-top: 0.25rem;'>
            Create an account to save your analyses and track your progress.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- If logged in, show profile ----
if is_logged_in():
    user = get_current_user()

    col_profile, col_actions = st.columns([2, 1])

    with col_profile:
        st.markdown(
            f"""
            <div style='background: rgba(26,26,46,0.8); border: 1px solid rgba(124,58,237,0.3);
                        border-radius: 20px; padding: 2rem; text-align: center;'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>👤</div>
                <div style='font-size: 1.5rem; font-weight: 800; color: var(--text-primary);'>{user['username']}</div>
                <div style='color: #64748B; margin-top: 0.25rem;'>{user['email']}</div>
                <div style='margin-top: 1.5rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;'>
                    <div style='background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.3);
                                border-radius: 12px; padding: 0.75rem 1.5rem; text-align: center;'>
                        <div style='font-size: 1.5rem; font-weight: 800; color: var(--text-primary);'>
                            {st.session_state.get('last_analysis') and 1 or 0}
                        </div>
                        <div style='font-size: 0.8rem; color: #64748B;'>Analyses</div>
                    </div>
                    <div style='background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3);
                                border-radius: 12px; padding: 0.75rem 1.5rem; text-align: center;'>
                        <div style='font-size: 1.5rem; font-weight: 800; color: #6EE7B7;'>
                            {st.session_state.get('last_analysis', {}).get('ats_result', {}).get('total_score', '--')}
                        </div>
                        <div style='font-size: 0.8rem; color: #64748B;'>Latest Score</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_actions:
        st.markdown("**⚙️ Account Actions**")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📁 View My History", use_container_width=True):
            st.switch_page("pages/6_📁_History.py")

        if st.button("📄 Analyze New Resume", use_container_width=True):
            st.switch_page("pages/1_📄_Resume_Analysis.py")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚪 Log Out", type="secondary", use_container_width=True):
            logout_user()
            st.success("✅ Logged out successfully!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("🔒 Your data is stored locally in a SQLite database on this machine.")

else:
    # ---- Auth Forms ----
    _, col_center, _ = st.columns([1, 2, 1])

    with col_center:
        tab_login, tab_register = st.tabs(["🔑 Log In", "✨ Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                st.markdown(
                    """<div style='text-align: center; margin-bottom: 1.5rem;'>
                        <div style='font-size: 1.3rem; font-weight: 700; color: var(--text-primary);'>Welcome back 👋</div>
                        <div style='color: #64748B; font-size: 0.9rem;'>Log in to your account</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")

                st.markdown("<br>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("🔑 Log In", use_container_width=True, type="primary")

                if submit_login:
                    if not username or not password:
                        st.error("Please enter your username and password.")
                    else:
                        user = get_user_by_username(username)
                        if user and verify_password(password, user.hashed_password):
                            login_user(user.id, user.username, user.email)
                            st.success(f"✅ Welcome back, {user.username}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password.")

        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("register_form", clear_on_submit=False):
                st.markdown(
                    """<div style='text-align: center; margin-bottom: 1.5rem;'>
                        <div style='font-size: 1.3rem; font-weight: 700; color: var(--text-primary);'>Join for free ✨</div>
                        <div style='color: #64748B; font-size: 0.9rem;'>Create your account to save analyses</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

                new_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
                new_email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
                new_password = st.text_input("Password", type="password", placeholder="Min 8 chars", key="reg_pass")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_confirm")

                st.markdown("<br>", unsafe_allow_html=True)
                submit_register = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")

                if submit_register:
                    errors = []

                    if not new_username or len(new_username) < 3:
                        errors.append("Username must be at least 3 characters")
                    if not validate_email(new_email):
                        errors.append("Invalid email address format")

                    is_strong, strength_msg = validate_password_strength(new_password)
                    if not is_strong:
                        errors.append(strength_msg)

                    if new_password != confirm_password:
                        errors.append("Passwords do not match")

                    if not errors:
                        # Check uniqueness
                        if get_user_by_username(new_username):
                            errors.append("Username already taken")
                        if get_user_by_email(new_email):
                            errors.append("Email already registered")

                    if errors:
                        for err in errors:
                            st.error(f"❌ {err}")
                    else:
                        hashed = hash_password(new_password)
                        new_user = create_user(new_username, new_email, hashed)
                        if new_user:
                            login_user(new_user.id, new_user.username, new_user.email)
                            st.success(f"✅ Account created! Welcome, {new_username}!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to create account. Please try again.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='text-align: center; color: #64748B; font-size: 0.8rem;'>
                🔒 Your data is stored locally. We never share your resume data.
            </div>
            """,
            unsafe_allow_html=True,
        )
