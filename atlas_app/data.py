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
    "P003": {
        "name": "Rahul Sharma",
        "designation": "Statistical Officer",
        "department": "Statistics & Programme Implementation",
        "role": "Statistical Officer",
        "qualifications": "M.Sc (Statistics)",
        "experience": "4 years",
        "training_history": ["Applied Statistics for Policy (2023)", "Python for Data Analysis (2024)"],
        "avatar": "📊",
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
    "Statistical Officer": [
        {"competency": "Statistics", "current": 65, "required": 80},
        {"competency": "Python", "current": 40, "required": 75},
        {"competency": "SQL", "current": 55, "required": 70},
        {"competency": "Data Analysis", "current": 60, "required": 80},
        {"competency": "Data Visualization", "current": 45, "required": 70},
    ],
}

MOCK_COURSE_CATALOG = [
    {"course": "Data Visualization with Power BI", "skill": "Data Visualization", "level": "Intermediate", "duration": "6 hrs"},
    {"course": "Advanced Statistical Methods", "skill": "Statistical Analysis", "level": "Advanced", "duration": "10 hrs"},
    {"course": "SQL for Government Analysts", "skill": "SQL / Data Querying", "level": "Intermediate", "duration": "5 hrs"},
    {"course": "Risk Assessment Frameworks", "skill": "Risk Assessment", "level": "Intermediate", "duration": "8 hrs"},
    {"course": "Budget Forecasting Essentials", "skill": "Budgeting & Forecasting", "level": "Advanced", "duration": "7 hrs"},
]

MOCK_QUIZ_BANK = [
    {"q": "What does SQL stand for?",
     "options": ["Structured Query Language", "Simple Query Logic", "Sequential Query Language", "Standard Query List"],
     "answer": 0},
    {"q": "Which chart type best shows a trend over time?",
     "options": ["Pie chart", "Line chart", "Scatter plot", "Heatmap"],
     "answer": 1},
    {"q": "A skill gap score is calculated as?",
     "options": ["Current - Required", "Required - Current", "Required / Current", "Current x Required"],
     "answer": 1},
    {"q": "Which is a key input for Budget Forecasting?",
     "options": ["Historical spend data", "Employee birthdays", "Office seating chart", "Font size"],
     "answer": 0},
]

PRIORITY_COLORS = {"High": "#FF5C7A", "Medium": "#FFB454", "Low": "#6C6CFF", "None": "#37D6A0"}


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
    """
    Member 2 — real gap formula.
    Supports both the 0-5 scale (Data Analyst / Financial Analyst mock data)
    and the 0-100 scale (Statistical Officer real competency framework) by
    normalizing the gap to a percentage of that competency's own scale
    before applying priority thresholds.
    """
    rows = []
    for c in competencies:
        current, required = c["current"], c["required"]
        gap = max(required - current, 0)

        # Infer the scale (0-5 vs 0-100) from the magnitude of the values.
        scale_max = 100 if max(current, required) > 5 else 5
        gap_percent = (gap / scale_max) * 100

        if gap <= 0:
            priority = "None"
        elif gap_percent >= 30:
            priority = "High"
        elif gap_percent >= 20:
            priority = "Medium"
        else:
            priority = "Low"

        rows.append({**c, "gap": gap, "priority": priority})
    return rows


def get_recommendations(gap_rows):
    """Member 5 → replace with real scoring/ranking logic."""
    recs = []
    for row in sorted(gap_rows, key=lambda r: -r["gap"]):
        if row["gap"] <= 0:
            continue
        for m in MOCK_COURSE_CATALOG:
            if m["skill"] == row["competency"]:
                recs.append({
                    **m,
                    "reason": f"Closes a {row['priority'].lower()}-priority gap of {row['gap']} level(s) in {row['competency']}.",
                    "priority": row["priority"],
                })
    return recs[:5]


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

def render_html(html: str):
    """
    Render a raw HTML snippet safely.

    Streamlit passes HTML through a Markdown parser before displaying it.
    If a multi-line HTML string contains a blank line followed by an
    indented line (very easy to end up with when building HTML from an
    indented Python f-string), Markdown's "indented code block" rule kicks
    in and the tag is shown as literal text instead of being rendered.

    To avoid that trap entirely, this collapses the snippet onto a single
    line (HTML ignores whitespace between tags anyway) before handing it
    to st.markdown with unsafe_allow_html=True.
    """
    compact = " ".join(line.strip() for line in html.strip().splitlines() if line.strip())
    st.markdown(compact, unsafe_allow_html=True)


def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

        :root {
            --atlas-accent: #6C6CFF;
            --atlas-accent-2: #37D6C4;
            --atlas-danger: #FF5C7A;
            --atlas-warning: #FFB454;
            --atlas-success: #37D6A0;
            --atlas-bg: #0B0D14;
            --atlas-surface: #141826;
            --atlas-surface-2: #1B2033;
            --atlas-border: rgba(255,255,255,0.08);
            --atlas-text: #F5F6FA;
            --atlas-text-dim: #9BA0B4;
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        h1, h2, h3, h4, h5, .atlas-hero-title {
            font-family: 'Sora', sans-serif !important;
            letter-spacing: -0.02em;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% -10%, rgba(108,108,255,0.16), transparent 45%),
                radial-gradient(circle at 90% 0%, rgba(55,214,196,0.10), transparent 40%),
                var(--atlas-bg);
        }

        /* Sidebar */
        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0D101B 0%, #0A0C14 100%);
            border-right: 1px solid var(--atlas-border);
        }
        div[data-testid="stSidebar"] * { color: var(--atlas-text) !important; }

        /* Generic card */
        .atlas-card {
            background: linear-gradient(180deg, var(--atlas-surface) 0%, rgba(20,24,38,0.7) 100%);
            border: 1px solid var(--atlas-border);
            border-radius: 16px;
            padding: 20px 22px;
            margin-bottom: 16px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.25);
            transition: transform .15s ease, border-color .15s ease;
        }
        .atlas-card:hover {
            border-color: rgba(108,108,255,0.35);
        }

        /* Hero banner */
        .atlas-hero {
            padding: 34px 36px;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(108,108,255,0.22) 0%, rgba(55,214,196,0.12) 55%, rgba(20,24,38,0.9) 100%);
            border: 1px solid var(--atlas-border);
            margin-bottom: 26px;
            position: relative;
            overflow: hidden;
        }
        .atlas-hero::after {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 100% 0%, rgba(255,255,255,0.06), transparent 60%);
        }
        .atlas-eyebrow {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            color: var(--atlas-accent-2);
            background: rgba(55,214,196,0.10);
            border: 1px solid rgba(55,214,196,0.25);
            padding: 5px 12px;
            border-radius: 999px;
            margin-bottom: 14px;
        }
        .atlas-hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--atlas-text);
            margin: 4px 0 8px 0;
        }
        .atlas-hero-sub {
            color: var(--atlas-text-dim);
            font-size: 1.02rem;
        }

        /* Badges */
        .atlas-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            color: white;
        }
        .atlas-badge-high { background: linear-gradient(135deg,#FF5C7A,#FF3D68); }
        .atlas-badge-medium { background: linear-gradient(135deg,#FFB454,#FF9D2E); }
        .atlas-badge-low { background: linear-gradient(135deg,#6C6CFF,#8A6CFF); }
        .atlas-badge-none { background: linear-gradient(135deg,#37D6A0,#20C997); }

        .atlas-metric-label {
            font-size: 0.8rem;
            color: var(--atlas-text-dim);
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        /* Metric tiles */
        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, var(--atlas-surface) 0%, rgba(20,24,38,0.55) 100%);
            border: 1px solid var(--atlas-border);
            border-radius: 16px;
            padding: 16px 18px 10px 18px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.22);
        }
        div[data-testid="stMetricLabel"] { color: var(--atlas-text-dim) !important; }
        div[data-testid="stMetricValue"] { color: var(--atlas-text) !important; font-family: 'Sora', sans-serif; }

        /* Buttons / links */
        .stButton > button, .stPageLink a, a[data-testid="stPageLink"] {
            border-radius: 12px !important;
            border: 1px solid var(--atlas-border) !important;
            background: linear-gradient(135deg, rgba(108,108,255,0.18), rgba(55,214,196,0.10)) !important;
            font-weight: 600 !important;
            transition: all .15s ease !important;
        }
        .stButton > button:hover, .stPageLink a:hover {
            border-color: var(--atlas-accent) !important;
            transform: translateY(-1px);
        }

        /* Progress bar */
        div[data-testid="stProgress"] > div > div {
            background: linear-gradient(90deg, var(--atlas-accent), var(--atlas-accent-2)) !important;
        }

        /* Dividers */
        hr { border-color: var(--atlas-border) !important; }

        /* Chat bubbles */
        div[data-testid="stChatMessage"] {
            background: var(--atlas-surface);
            border: 1px solid var(--atlas-border);
            border-radius: 14px;
        }

        /* Journey / list rows */
        .atlas-row {
            display:flex;
            align-items:center;
            gap:18px;
            padding:16px 18px;
            margin-bottom:10px;
            border-radius:14px;
            background: var(--atlas-surface);
            border: 1px solid var(--atlas-border);
            transition: border-color .15s ease;
        }
        .atlas-row:hover { border-color: rgba(108,108,255,0.35); }
        .atlas-row-index {
            min-width:42px;
            height:42px;
            display:flex;
            align-items:center;
            justify-content:center;
            border-radius:50%;
            background: linear-gradient(135deg, rgba(108,108,255,0.3), rgba(55,214,196,0.2));
            color: var(--atlas-text);
            font-weight:700;
            font-family: 'Sora', sans-serif;
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