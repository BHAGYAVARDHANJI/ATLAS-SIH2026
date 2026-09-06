"""
ATLAS — Authentication Layer
SIH26101 One-Day Prototype

Simple username/password authentication backed by SQLite (db.py).
Passwords are never stored in plain text — each password is hashed
with PBKDF2-HMAC-SHA256 + a per-user random salt (both from Python's
stdlib `hashlib`, so no extra dependency is needed).

This module ONLY handles auth logic (hashing, verifying, session
flags). It does not render any UI — that lives in streamlit_app.py's
login/signup form.
"""

import hashlib
import hmac
import os

import streamlit as st

import db

PBKDF2_ITERATIONS = 200_000


# ============================================================
# PASSWORD HASHING
# ============================================================

def _hash_password(password: str, salt: bytes) -> str:
    """Return a hex-encoded PBKDF2-HMAC-SHA256 hash of `password` using `salt`."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return dk.hex()


def hash_new_password(password: str) -> tuple[str, str]:
    """Generate a fresh salt + hash for a new password. Returns (salt_hex, hash_hex)."""
    salt = os.urandom(16)
    return salt.hex(), _hash_password(password, salt)


def verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    """Check a login attempt's password against the stored salt+hash."""
    salt = bytes.fromhex(salt_hex)
    candidate_hash = _hash_password(password, salt)
    # constant-time comparison to avoid timing attacks
    return hmac.compare_digest(candidate_hash, expected_hash_hex)


# ============================================================
# SIGNUP / LOGIN
# ============================================================

def signup(username: str, password: str) -> tuple[bool, str]:
    """
    Create a new user account.
    Returns (success, message).
    """
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    if db.get_user(username) is not None:
        return False, "That username is already taken."

    salt_hex, hash_hex = hash_new_password(password)
    db.create_user(username, salt_hex, hash_hex)
    return True, "Account created! You can now log in."


def login(username: str, password: str) -> tuple[bool, str]:
    """
    Verify credentials and, on success, set Streamlit session state.
    Returns (success, message).
    """
    username = username.strip()
    user = db.get_user(username)
    if user is None:
        return False, "No account found with that username."

    if not verify_password(password, user["password_salt"], user["password_hash"]):
        return False, "Incorrect password."

    st.session_state.authenticated = True
    st.session_state.auth_username = username
    return True, "Logged in successfully."


def logout():
    """Clear the authenticated session."""
    for key in ("authenticated", "auth_username"):
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated"))