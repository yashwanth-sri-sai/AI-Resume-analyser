"""
utils/auth.py
Authentication: password hashing, session management, JWT tokens.
"""

import os
import datetime
import hashlib
import hmac
import base64
from typing import Optional

import streamlit as st


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt."""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    except ImportError:
        # Fallback to PBKDF2 if bcrypt not available
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return base64.b64encode(salt + key).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        import bcrypt
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ImportError:
        # Fallback verification
        try:
            decoded = base64.b64decode(hashed.encode("utf-8"))
            salt = decoded[:32]
            stored_key = decoded[32:]
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
            return hmac.compare_digest(key, stored_key)
        except Exception:
            return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Check password meets minimum requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    return True, "Password is strong."


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    import re
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def login_user(user_id: int, username: str, email: str):
    """Set session state for logged-in user."""
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user_id
    st.session_state["username"] = username
    st.session_state["email"] = email
    st.session_state["login_time"] = datetime.datetime.now().isoformat()


def logout_user():
    """Clear session state for logout."""
    for key in ["logged_in", "user_id", "username", "email", "login_time"]:
        if key in st.session_state:
            del st.session_state[key]


def is_logged_in() -> bool:
    """Check if user is currently logged in."""
    return st.session_state.get("logged_in", False)


def get_current_user() -> Optional[dict]:
    """Get the current logged-in user's info."""
    if not is_logged_in():
        return None
    return {
        "id": st.session_state.get("user_id"),
        "username": st.session_state.get("username"),
        "email": st.session_state.get("email"),
    }


def require_login(redirect_message: str = "Please log in to access this feature."):
    """Display login prompt if user is not logged in."""
    if not is_logged_in():
        st.warning(redirect_message)
        st.info("👉 Go to the **Authentication** page to create an account or log in.")
        st.stop()
