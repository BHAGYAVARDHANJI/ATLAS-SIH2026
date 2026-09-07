"""ATLAS authentication and learner-account mapping."""

import hashlib
import hmac
import os

import streamlit as st

import db

PBKDF2_ITERATIONS = 200_000


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS).hex()


def hash_new_password(password: str) -> tuple[str, str]:
    salt = os.urandom(16)
    return salt.hex(), _hash_password(password, salt)


def verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    try:
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    return hmac.compare_digest(_hash_password(password, salt), expected_hash_hex)


def _normalise_username(username: str) -> str:
    return " ".join(username.strip().lower().split())


def _clear_app_state():
    for key in (
        "gap_rows", "current_quiz", "quiz_source",
        "quiz_answers", "quiz_submitted", "quiz_score", "quiz_version",
        "atlas_chat_messages",
    ):
        st.session_state.pop(key, None)


def signup(username: str, password: str, profile_code: str) -> tuple[bool, str]:
    username = _normalise_username(username)
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    if db.get_user(username) is not None:
        return False, "That username is already taken."
    if not db.get_profile(profile_code):
        return False, "Please select a valid learner profile."
    if db.get_user_by_profile(profile_code) is not None:
        return False, "That learner profile is already linked to another account."

    salt_hex, hash_hex = hash_new_password(password)
    db.create_user(username, salt_hex, hash_hex, profile_code)
    return True, "Account created! You can now log in."


def login(username: str, password: str) -> tuple[bool, str]:
    username = _normalise_username(username)
    user = db.get_user(username)
    if user is None:
        return False, "No account found with that username."
    if not verify_password(password, user["password_salt"], user["password_hash"]):
        return False, "Incorrect password."

    profile_code = user["profile_code"]
    if not profile_code:
        return False, "This account is not linked to a learner profile. Please create/link the account again."
    if db.get_profile(profile_code) is None:
        return False, "The learner profile linked to this account no longer exists."

    _clear_app_state()
    st.session_state.authenticated = True
    st.session_state.auth_username = user["username"]
    st.session_state.auth_profile_id = profile_code
    st.session_state.quiz_version = 0
    return True, "Logged in successfully."


def logout():
    _clear_app_state()
    for key in ("authenticated", "auth_username", "auth_profile_id"):
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated")) and bool(st.session_state.get("auth_profile_id"))


def current_profile_id() -> str | None:
    return st.session_state.get("auth_profile_id")
