"""
ATLAS — Shared Data Layer
Member 1 owns this file's STRUCTURE. Function names + return shapes are
kept identical to the original mock version so the UI never breaks.

Member 4 handoff: get_profile, get_competency_profile, save_progress and
the course catalogue behind get_recommendations now come from db.py
(SQLite) instead of hardcoded MOCK_* dictionaries.
"""

import random

import streamlit as st

import auth
import db
import quiz as ai_quiz

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
    {"q": "In Python, which library is most commonly used for tabular data analysis?",
     "options": ["pandas", "turtle", "tkinter", "socket"],
     "answer": 0},
    {"q": "In a SQL query with WHERE, GROUP BY and HAVING together, which clause is evaluated first?",
     "options": ["HAVING", "GROUP BY", "WHERE", "They all run at the same time"],
     "answer": 2},
    {"q": "In statistics, a p-value below 0.05 is generally taken to mean:",
     "options": ["The result is statistically significant", "The sample size is too small",
                 "The data is perfectly normal", "The experiment failed"],
     "answer": 0},
    {"q": "Risk Assessment primarily involves:",
     "options": ["Identifying risks and evaluating their likelihood and impact", "Formatting a spreadsheet",
                 "Designing a company logo", "Scheduling annual leave"],
     "answer": 0},
    {"q": "Regulatory Compliance mainly ensures that an organization:",
     "options": ["Follows the laws, rules and standards that apply to it", "Maximizes profit at any cost",
                 "Avoids all documentation", "Reduces staff training"],
     "answer": 0},
    {"q": "A good official report should primarily be:",
     "options": ["Vague and as long as possible", "Clear, well-structured and evidence-based",
                 "Written only in technical jargon", "Free of any supporting data"],
     "answer": 1},
    {"q": "Financial Reporting is best described as:",
     "options": ["Recording and presenting an organization's financial performance",
                 "Designing office layouts", "Managing IT infrastructure", "Writing marketing copy"],
     "answer": 0},
    {"q": "A heatmap is most useful for showing:",
     "options": ["Intensity or patterns across two categorical dimensions", "The exact value of a single number",
                 "A strict chronological timeline", "A simple yes/no comparison"],
     "answer": 0},
    {"q": "In Python, which keyword is used to define a function?",
     "options": ["func", "def", "function", "lambda only"],
     "answer": 1},
    {"q": "An INNER JOIN in SQL returns:",
     "options": ["Only rows that match in both tables", "All rows from both tables regardless of a match",
                 "Only rows from the left table", "Only rows with NULL values"],
     "answer": 0},
    {"q": "Which measure of central tendency is most affected by extreme outliers?",
     "options": ["Mean", "Median", "Mode", "None of them are affected"],
     "answer": 0},
]


PRIORITY_COLORS = {"High": "#FF5C7A", "Medium": "#FFB454", "Low": "#6C6CFF", "None": "#37D6A0"}

# ============================================================
# FUNCTIONS (Member handoff points)
# ============================================================

def get_profile(profile_id):
    """Member 4 → now backed by SQLite (db.get_profile)."""
    return db.get_profile(profile_id)


def get_competency_profile(profile_id):
    """
    Member 2 → competency levels for this specific learner, from SQLite.

    NOTE: this now takes the profile_id (e.g. "P001"), not the role
    string, because real learners of the same role can be at different
    levels. Call sites were updated to pass profile["id"] accordingly.
    """
    return db.get_competency_profile(profile_id)


def calculate_skill_gap(competencies):
    """
    Member 2 — real gap formula.
    Supports both the 0-5 scale (Data Analyst / Financial Analyst) and
    the 0-100 scale (Statistical Officer) by normalizing the gap to a
    percentage of that competency's own scale before applying priority
    thresholds.
    """
    rows = []
    for c in competencies:
        current, required = c["current"], c["required"]
        gap = max(required - current, 0)

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
    """
    Return learning recommendations for the learner's actual skill gaps.

    Recommendations come from the SQLite/iGOT catalogue so the catalogue
    used here stays in sync with db.py. Results are ranked by the largest
    gap first, and skills that are already at the required level are ignored.
    """
    recs = []

    for row in sorted(gap_rows, key=lambda r: (-r["gap"], r["competency"])):
        if row["gap"] <= 0:
            continue

        courses = db.get_courses(skill=row["competency"])

        for course in courses:
            recs.append({
                "course": course["title"],
                "skill": course["skill"],
                "level": course.get("level") or "Recommended",
                "duration": (
                    f"{course['duration_hours']:g} hrs"
                    if course.get("duration_hours") is not None
                    else "Self-paced"
                ),
                "description": course.get("description", ""),
                "source": course.get("source", "iGOT"),
                "reason": (
                    f"Closes a {row['priority'].lower()}-priority gap of "
                    f"{row['gap']} level(s) in {row['competency']}."
                ),
                "priority": row["priority"],
                "gap": row["gap"],
            })

    return recs[:6]


def generate_quiz(n=3, profile_id=None):
    """
    Member 3 — tries a real AI-generated quiz (Gemini) personalised to
    the learner's current skill gaps. Falls back to the static
    MOCK_QUIZ_BANK if there's no API key, the call fails, or the
    response can't be parsed — the P0 flow must never break just
    because the AI call didn't work.

    Returns: (questions, source) where source is "ai" or "fallback".
    """
    topics = []
    if profile_id:
        try:
            comps = get_competency_profile(profile_id)
            gaps = calculate_skill_gap(comps)
            topics = [
                g["competency"]
                for g in sorted(gaps, key=lambda g: -g["gap"])
                if g["gap"] > 0
            ][:3]
        except Exception:
            topics = []

    try:
        questions = ai_quiz.generate_ai_quiz(topics, n)
        return questions, "ai"
    except Exception:
        return random.sample(MOCK_QUIZ_BANK, min(n, len(MOCK_QUIZ_BANK))), "fallback"


def save_progress(profile_id, score, total):
    """Member 4 → now persisted in SQLite (db.save_assessment) instead of
    only living in st.session_state, so it survives an app restart."""
    db.save_assessment(profile_id, score, total, quiz_title="ATLAS Quiz")


def get_progress_log(profile_id):
    """New helper for the Progress page — reads persisted attempts from SQLite."""
    return db.get_assessments(profile_id)


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


def get_theme() -> str:
    """Current UI theme for this session: 'dark' (default) or 'light'."""
    return st.session_state.get("atlas_theme", "dark")


def set_theme(theme: str):
    st.session_state.atlas_theme = "light" if theme == "light" else "dark"


def theme_toggle_control(container=st.sidebar):
    """Render a ☀️ / 🌙 theme switch. Call once per page, in the sidebar."""
    current = get_theme()
    labels = {"dark": "🌙 Dark mode", "light": "☀️ Light mode"}
    choice = container.radio(
        "Appearance",
        options=["dark", "light"],
        index=0 if current == "dark" else 1,
        format_func=lambda t: labels[t],
        key="atlas_theme_choice",
        horizontal=True,
        label_visibility="collapsed",
    )
    if choice != current:
        set_theme(choice)
        st.rerun()


def inject_custom_css():
    theme = get_theme()

    if theme == "light":
        palette = {
            "bg": "#F5F7FB",
            "bg-glow-1": "rgba(108,108,255,0.10)",
            "bg-glow-2": "rgba(55,214,196,0.08)",
            "surface": "#FFFFFF",
            "surface-2": "#F0F2F8",
            "border": "rgba(15,18,30,0.10)",
            "text": "#171A23",
            "text-dim": "#5B6072",
            "sidebar-grad": "linear-gradient(180deg, #FFFFFF 0%, #F2F4FA 100%)",
            "shadow": "0 6px 20px rgba(30,34,60,0.08)",
        }
    else:
        palette = {
            "bg": "#0B0D14",
            "bg-glow-1": "rgba(108,108,255,0.16)",
            "bg-glow-2": "rgba(55,214,196,0.10)",
            "surface": "#141826",
            "surface-2": "#1B2033",
            "border": "rgba(255,255,255,0.08)",
            "text": "#F5F6FA",
            "text-dim": "#9BA0B4",
            "sidebar-grad": "linear-gradient(180deg, #0D101B 0%, #0A0C14 100%)",
            "shadow": "0 6px 24px rgba(0,0,0,0.25)",
        }

    dynamic_css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

        :root {{
            --atlas-accent: #6C6CFF;
            --atlas-accent-2: #37D6C4;
            --atlas-danger: #FF5C7A;
            --atlas-warning: #FFB454;
            --atlas-success: #37D6A0;
            --atlas-bg: {palette['bg']};
            --atlas-surface: {palette['surface']};
            --atlas-surface-2: {palette['surface-2']};
            --atlas-border: {palette['border']};
            --atlas-text: {palette['text']};
            --atlas-text-dim: {palette['text-dim']};
        }}

        /* ---- Remove default Streamlit chrome so this reads as a real app ---- */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        [data-testid="stToolbar"] {{ visibility: hidden; }}
        [data-testid="stDecoration"] {{ display: none; }}
        [data-testid="stStatusWidget"] {{ visibility: hidden; }}

        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }}

        h1, h2, h3, h4, h5, .atlas-hero-title {{
            font-family: 'Sora', sans-serif !important;
            letter-spacing: -0.02em;
        }}

        .stApp {{
            background:
                radial-gradient(circle at 12% -10%, var(--atlas-glow-1, {palette['bg-glow-1']}), transparent 45%),
                radial-gradient(circle at 90% 0%, var(--atlas-glow-2, {palette['bg-glow-2']}), transparent 40%),
                var(--atlas-bg);
        }}
        .stApp, .stApp p, .stApp span, .stApp label, .stApp li {{ color: var(--atlas-text); }}

        div[data-testid="stSidebar"] {{
            background: {palette['sidebar-grad']};
            border-right: 1px solid var(--atlas-border);
        }}
        div[data-testid="stSidebar"] * {{ color: var(--atlas-text) !important; }}

        /* ---- Inputs / widgets follow the chosen theme too ---- */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-baseweb="select"] > div,
        div[data-testid="stNumberInput"] input {{
            background-color: var(--atlas-surface) !important;
            color: var(--atlas-text) !important;
            border-color: var(--atlas-border) !important;
        }}
        div[data-testid="stForm"] {{
            background: var(--atlas-surface);
            border: 1px solid var(--atlas-border);
            border-radius: 16px;
            padding: 18px 20px;
        }}
        div[data-testid="stExpander"], div[data-baseweb="tab-list"] {{
            background: var(--atlas-surface);
            border: 1px solid var(--atlas-border);
            border-radius: 12px;
        }}
        div[data-testid="stDataFrame"] {{ border: 1px solid var(--atlas-border); border-radius: 12px; }}

        /* ---- Give the page a readable max-width like a real product, not an edge-to-edge admin panel ---- */
        div[data-testid="stAppViewBlockContainer"] {{
            max-width: 1200px;
        }}
        </style>
    """

    static_css = """
        <style>
        .atlas-step-track {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0;
            background: var(--atlas-surface);
            border: 1px solid var(--atlas-border);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 22px;
        }
        .atlas-step {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--atlas-text);
            white-space: nowrap;
        }
        .atlas-step-dot {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.72rem;
            font-weight: 800;
            color: white;
            background: linear-gradient(135deg, var(--atlas-accent), var(--atlas-accent-2));
            flex-shrink: 0;
        }
        .atlas-step-line {
            flex: 1;
            min-width: 24px;
            height: 2px;
            background: var(--atlas-border);
            margin: 0 14px;
        }
        .atlas-card {
            background: var(--atlas-surface);
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

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, var(--atlas-surface) 0%, rgba(20,24,38,0.55) 100%);
            border: 1px solid var(--atlas-border);
            border-radius: 16px;
            padding: 16px 18px 10px 18px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.22);
        }
        div[data-testid="stMetricLabel"] { color: var(--atlas-text-dim) !important; }
        div[data-testid="stMetricValue"] { color: var(--atlas-text) !important; font-family: 'Sora', sans-serif; }

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

        div[data-testid="stProgress"] > div > div {
            background: linear-gradient(90deg, var(--atlas-accent), var(--atlas-accent-2)) !important;
        }

        hr { border-color: var(--atlas-border) !important; }

        div[data-testid="stChatMessage"] {
            background: var(--atlas-surface);
            border: 1px solid var(--atlas-border);
            border-radius: 14px;
        }

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
    """

    st.markdown(dynamic_css + static_css, unsafe_allow_html=True)


def require_login():
    """Stop protected pages unless a valid authenticated learner exists."""
    if not auth.is_authenticated():
        st.warning("⚠️ Please log in first.")
        st.stop()


def require_profile():
    """Return the learner profile linked to the authenticated account."""
    require_login()
    profile_id = auth.current_profile_id()
    if not profile_id:
        st.error("⚠️ Your account is not linked to a learner profile.")
        st.stop()

    profile = get_profile(profile_id)
    if profile is None:
        st.error("⚠️ The linked learner profile could not be found.")
        st.stop()

    return profile


def sidebar_profile_switcher():
    """Render authenticated learner identity, theme control and logout."""
    require_login()
    profile_id = auth.current_profile_id()
    profile = get_profile(profile_id) if profile_id else None
    if profile is None:
        st.error("⚠️ No valid learner is linked to this account.")
        st.stop()

    # The authenticated account is the single source of truth for the learner.
    # Do not assign to a widget-backed session-state key here.
    st.sidebar.markdown("## 🎓 ATLAS")
    st.sidebar.caption("Adaptive Learning Intelligence")
    st.sidebar.markdown(
        f'''<div class="atlas-card" style="padding:14px 16px; margin:14px 0;">
            <div style="font-size:1.9rem;">{profile["avatar"]}</div>
            <div style="font-weight:800; font-size:1.05rem; margin-top:4px;">{profile["name"]}</div>
            <div style="color:var(--atlas-text-dim); font-size:.82rem; margin-top:2px;">{profile["role"]}</div>
            <div style="color:var(--atlas-text-dim); font-size:.75rem; margin-top:8px;">Signed in as <b>{st.session_state.get("auth_username", "User")}</b></div>
        </div>''' ,
        unsafe_allow_html=True,
    )
    theme_toggle_control(st.sidebar)
    if st.sidebar.button("🚪 Log Out", width="stretch", key="atlas_logout"):
        auth.logout()
        st.rerun()
    return profile_id
