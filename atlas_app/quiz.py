"""
ATLAS — Member 3: AI Quiz Layer
SIH26101 One-Day Prototype

Generates multiple-choice quiz questions using Google's Gemini API
(free tier via Google AI Studio — https://aistudio.google.com/apikey,
no credit card required).

This module ONLY talks to the LLM. It never decides what happens if the
call fails — that fallback logic lives in atlas_app/data.py, per the
plan's "keep a fallback quiz dataset" rule.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _get_api_key() -> Optional[str]:
    """Looks in Streamlit secrets first, then the environment."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY")


def generate_ai_quiz(topics: List[str], n: int = 3) -> List[Dict[str, Any]]:
    """
    Ask Gemini for `n` multiple-choice questions covering `topics`
    (competency/skill names the learner has a gap in).

    Returns: [{"q": str, "options": [str, str, str, str], "answer": int}, ...]

    Raises on ANY failure (missing key, network error, bad JSON, etc.)
    so the caller (data.generate_quiz) can fall back to the mock bank —
    this function intentionally does not swallow errors itself.
    """
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError(
            "No GEMINI_API_KEY found. Add it to atlas_app/.streamlit/secrets.toml "
            "or set it as an environment variable."
        )

    topic_line = ", ".join(topics) if topics else "general workplace skills"

    prompt = f"""You are creating a short multiple-choice quiz for a government
employee training platform called ATLAS.

Write exactly {n} multiple-choice questions that test practical,
job-relevant understanding of: {topic_line}.

Rules:
- Each question has exactly 4 answer options.
- Exactly one option is correct.
- Keep questions concise, unambiguous and workplace-relevant.
- Return ONLY a JSON array, no prose, no markdown fences, in this exact shape:
[
  {{"q": "question text", "options": ["A", "B", "C", "D"], "answer": 0}}
]
"answer" is the 0-based index of the correct option in "options"."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "response_mime_type": "application/json",
        },
    }

    response = requests.post(
        GEMINI_URL,
        params={"key": api_key},
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    # Some models still wrap output in ```json fences despite the instruction.
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()

    raw_questions = json.loads(text)

    cleaned = []
    for q in raw_questions:
        if not isinstance(q, dict):
            continue
        question_text = str(q.get("q", "")).strip()
        options = q.get("options")
        answer = q.get("answer")

        if not question_text or not isinstance(options, list) or len(options) < 2:
            continue
        if not isinstance(answer, int) or not (0 <= answer < len(options)):
            continue

        cleaned.append({"q": question_text, "options": [str(o) for o in options], "answer": answer})

    if not cleaned:
        raise ValueError("Gemini response contained no valid questions")

    return cleaned[:n]