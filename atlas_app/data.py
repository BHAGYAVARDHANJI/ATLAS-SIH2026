"""
ATLAS — Shared Data Layer
Member 1 owns this file's STRUCTURE. Replace the body of each function
with real calls from Member 2 (competency/gap), Member 3 (quiz),
Member 4 (DB), Member 5 (recommendations) as they hand off code.
Keep function names + return shapes identical so the UI never breaks.
"""

import random
import streamlit as st

# ============================================================
# MOCK DATA (swap sources later, keep shapes identical)
# ============================================================

MOCK_PROFILES = {
    "P001": {
        "name": "Ananya Sharma",
        "designation": "Assistant Section Officer",
        "department": "Rural Development",
        "role": "Data Analyst",
        "qualifications": "B.Tech (CSE)",
        "experience": "3 years",
        "training_history": ["Basics of Data Analytics (2024)", "MS Excel Advanced (2023)"],
        "avatar": "🧑‍💼",
    },
    "P002": {
        "name": "Rohit Verma",
        "designation": "Section Officer",
        "department": "Finance",
        "role": "Financial Analyst",
        "qualifications": "MBA (Finance)",
        "experience": "6 years",
        "training_history": ["Public Financial Management (2022)"],
        "avatar": "👨‍💼",
    },
}

MOCK_COMPETENCIES = {
    "Data Analyst": [
        {"competency": "Data Visualization", "current": 2, "required": 4},
        {"competency": "SQL / Data Querying", "current": 3, "required": 4},
        {"competency": "Statistical Analysis", "current": 2, "required": 5},
        {"competency": "Report Writing", "current": 4, "required": 4},
    ],
    "Financial Analyst": [
        {"competency": "Budgeting & Forecasting", "current": 3, "required": 5},
        {"competency": "Financial Reporting", "current": 4, "required": 4},
        {"competency": "Risk Assessment", "current": 2, "required": 4},
        {"competency": "Regulatory Compliance", "current": 3, "required": 3},
    ],
}

MOCK_COURSE_CATALOG = [

    # -------- Data Analyst Courses --------

    {
        "course": "Data Visualization with Power BI",
        "skill": "Data Visualization",
        "level": "Intermediate",
        "duration": "6 hrs"
    },

    {
        "course": "SQL for Data Analysts",
        "skill": "SQL / Data Querying",
        "level": "Intermediate",
        "duration": "6 hrs"
    },

    {
        "course": "Advanced Statistical Analysis",
        "skill": "Statistical Analysis",
        "level": "Advanced",
        "duration": "10 hrs"
    },

    {
        "course": "Professional Report Writing",
        "skill": "Report Writing",
        "level": "Intermediate",
        "duration": "5 hrs"
    },

    # -------- Statistical Officer Courses --------

    {
        "course": "Advanced Statistics for Officers",
        "skill": "Statistical Analysis",
        "level": "Advanced",
        "duration": "10 hrs"
    },

    {
        "course": "Python for Data Analysis",
        "skill": "Python",
        "level": "Intermediate",
        "duration": "8 hrs"
    },

    {
        "course": "SQL for Data Management",
        "skill": "SQL / Data Querying",
        "level": "Intermediate",
        "duration": "6 hrs"
    },

    {
        "course": "Data Analysis Fundamentals",
        "skill": "Data Analysis",
        "level": "Intermediate",
        "duration": "7 hrs"
    }
]

PRIORITY_COLORS = {"High": "#FF4B4B", "Medium": "#FFA500", "Low": "#4F8BF9", "None": "#2ECC71"}


# ============================================================
# FUNCTIONS (Member handoff points)
# ============================================================

def get_profile(profile_id):
    """Member 4 → replace with real DB read."""
    return MOCK_PROFILES.get(profile_id)


def get_competency_profile(role):
    """Member 2 → replace with real competency mapping."""
    return MOCK_COMPETENCIES.get(role, [])


def calculate_skill_gap(competencies):
    """Member 2 → replace with the real gap formula."""
    rows = []
    for c in competencies:
        gap = c["required"] - c["current"]
        if gap >= 3:
            priority = "High"
        elif gap == 2:
            priority = "Medium"
        elif gap <= 0:
            priority = "None"
        else:
            priority = "Low"
        rows.append({**c, "gap": gap, "priority": priority})
    return rows


def get_recommendations(gap_rows):
    """
    Member 5 — Personalized Course Recommendation Engine.

    Courses are selected according to the learner's skill gaps
    and ranked from highest gap to lowest gap.
    """

    recommendations = []

    # Sort skills by biggest gap first
    sorted_gaps = sorted(
        gap_rows,
        key=lambda row: row["gap"],
        reverse=True
    )

    for row in sorted_gaps:

        # No gap = no course needed
        if row["gap"] <= 0:
            continue

               # Find the best matching course for this competency
        for course in MOCK_COURSE_CATALOG:

            if course["skill"] == row["competency"]:

                recommendations.append({
                    **course,

                    "priority": row["priority"],

                    "gap": row["gap"],

                    "reason": (
                        f"Your current level is {row['current']} "
                        f"while the required level is {row['required']}. "
                        f"This creates a {row['gap']} level gap in "
                        f"{row['competency']}."
                    )
                })

                # Only one course per skill gap
                break

    # Return maximum 5 recommendations
    return recommendations[:5]

def generate_quiz(n=3):
    """Member 3 → replace with LLM-generated MCQs; keep this as fallback."""
    return random.sample(MOCK_QUIZ_BANK, min(n, len(MOCK_QUIZ_BANK)))


def save_progress(profile_id, score, total):
    """Member 4 → replace with real DB write."""
    if "progress_log" not in st.session_state:
        st.session_state.progress_log = []
    st.session_state.progress_log.append(
        {"profile_id": profile_id, "score": score, "total": total}
    )


# ============================================================
# SHARED UI HELPERS
# ============================================================

def inject_custom_css():
    st.markdown("""
        <style>
        .atlas-card {
            background-color: #1B1F27;
            border: 1px solid #2A2F3A;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 14px;
        }
        .atlas-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
        }
        .atlas-metric-label {
            font-size: 0.85rem;
            color: #9BA3AF;
        }
        div[data-testid="stSidebar"] {
            border-right: 1px solid #2A2F3A;
        }
        </style>
    """, unsafe_allow_html=True)


def require_profile():
    """Guards pages that need a profile selected first."""
    if "selected_profile" not in st.session_state or st.session_state.selected_profile is None:
        st.warning("⚠️ No learner profile selected yet. Go to the Home page first.")
        st.stop()
    return get_profile(st.session_state.selected_profile)


def sidebar_profile_switcher():
    st.sidebar.markdown("### 🎓 ATLAS")
    st.sidebar.caption("Smart Education Platform")
    st.sidebar.divider()
    profile_id = st.sidebar.selectbox(
        "Active Learner",
        options=list(MOCK_PROFILES.keys()),
        format_func=lambda pid: f"{MOCK_PROFILES[pid]['avatar']} {MOCK_PROFILES[pid]['name']}",
        key="selected_profile",
    )
    return profile_id
