import streamlit as st
from skill_gap import calculate_skill_gap


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ATLAS | Skill Intelligence",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #f5f7fb;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }


    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    .atlas-logo {
        font-size: 34px;
        font-weight: 800;
        letter-spacing: 2px;
        color: #ffffff !important;
        margin-top: 10px;
    }

    .atlas-subtitle {
        color: #9ca3af !important;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 3px;
        margin-bottom: 35px;
    }

    .sidebar-heading {
        color: #9ca3af !important;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }


    /* ---------- MAIN HEADER ---------- */

    .main-title {
        color: #111827;
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 3px;
    }

    .main-subtitle {
        color: #64748b;
        font-size: 15px;
        margin-bottom: 28px;
    }


    /* ---------- SECTION ---------- */

    .section-title {
        color: #111827;
        font-size: 20px;
        font-weight: 750;
        margin-top: 22px;
        margin-bottom: 12px;
    }

    .section-description {
        color: #64748b;
        font-size: 13px;
        margin-top: -7px;
        margin-bottom: 16px;
    }


    /* ---------- PROFILE CARD ---------- */

    .profile-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
    }

    .profile-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }

    .profile-value {
        color: #111827;
        font-size: 17px;
        font-weight: 700;
    }


    /* ---------- STREAMLIT INPUTS ---------- */

    .stTextInput label,
    .stSelectbox label {
        color: #334155 !important;
        font-weight: 600 !important;
    }

    .stTextInput input {
        color: #111827 !important;
        background: #ffffff !important;
        border: 1px solid #dbe2ea !important;
        border-radius: 9px !important;
    }

    div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: #dbe2ea !important;
        border-radius: 9px !important;
    }


    /* ---------- SLIDER ---------- */

    div[data-testid="stSlider"] label {
        color: #1e293b !important;
        font-weight: 700 !important;
    }

    div[data-testid="stSlider"] label p {
        color: #1e293b !important;
        font-weight: 700 !important;
    }

    div[data-testid="stSlider"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 13px;
        padding: 14px 18px 8px 18px;
        margin-bottom: 12px;
    }


    /* ---------- BUTTON ---------- */

    .stButton > button {
        width: 100%;
        height: 48px;
        border-radius: 10px;
        border: none;
        background: #2563eb;
        color: white;
        font-size: 15px;
        font-weight: 700;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        background: #1d4ed8;
        color: white;
    }


    /* ---------- METRIC CARDS ---------- */

    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 19px;
        min-height: 112px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
    }

    .metric-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .metric-value {
        color: #111827;
        font-size: 29px;
        font-weight: 800;
        margin-top: 8px;
    }


    /* ---------- RESULT CARD ---------- */

    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 19px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 9px rgba(15, 23, 42, 0.03);
    }

    .result-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 13px;
    }

    .result-name {
        color: #111827;
        font-size: 16px;
        font-weight: 750;
    }

    .result-info {
        color: #64748b;
        font-size: 12px;
        margin-top: 4px;
    }

    .result-gap {
        color: #334155;
        font-size: 13px;
        font-weight: 700;
    }


    /* ---------- PRIORITY BADGES ---------- */

    .high {
        background: #fee2e2;
        color: #b91c1c;
        padding: 6px 11px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.4px;
    }

    .medium {
        background: #fef3c7;
        color: #a16207;
        padding: 6px 11px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.4px;
    }

    .low {
        background: #dcfce7;
        color: #15803d;
        padding: 6px 11px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.4px;
    }


    /* ---------- PROGRESS BAR ---------- */

    .progress-background {
        width: 100%;
        height: 8px;
        background: #e8edf3;
        border-radius: 20px;
        overflow: hidden;
    }

    .progress-current {
        height: 100%;
        background: #2563eb;
        border-radius: 20px;
    }

    .progress-labels {
        display: flex;
        justify-content: space-between;
        color: #64748b;
        font-size: 11px;
        margin-top: 6px;
    }


    /* ---------- RECOMMENDATION BOX ---------- */

    .focus-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        padding: 18px 20px;
        margin-top: 8px;
    }

    .focus-title {
        color: #1e40af;
        font-size: 15px;
        font-weight: 750;
        margin-bottom: 5px;
    }

    .focus-text {
        color: #475569;
        font-size: 13px;
        line-height: 1.5;
    }


    /* ---------- DIVIDER ---------- */

    .custom-divider {
        height: 1px;
        background: #e2e8f0;
        margin: 26px 0;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="atlas-logo">ATLAS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="atlas-subtitle">'
        'AI-powered Skill Intelligence Platform'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-heading">Workspace</div>',
        unsafe_allow_html=True
    )

    st.radio(
        "Navigation",
        [
            "Skill Gap Analysis",
            "Learning Recommendations",
            "Assessment",
            "Progress"
        ],
        label_visibility="collapsed"
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="main-title">Skill Gap Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Assess current competencies against role-specific requirements '
    'and identify development priorities.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# EMPLOYEE PROFILE
# =========================================================

st.markdown(
    '<div class="section-title">Employee Profile</div>',
    unsafe_allow_html=True
)

profile_col1, profile_col2 = st.columns(2)

with profile_col1:
    employee_name = st.text_input(
        "Employee Name",
        value="Rahul Sharma"
    )

with profile_col2:
    role = st.selectbox(
        "Current Role",
        ["Statistical Officer"]
    )


# =========================================================
# SKILL INPUT
# =========================================================

st.markdown(
    '<div class="section-title">Current Competencies</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Set the current proficiency level for each competency.'
    '</div>',
    unsafe_allow_html=True
)


skills = [
    "Statistics",
    "Python",
    "SQL",
    "Data Analysis",
    "Data Visualization"
]

current_skills = {}

col1, col2 = st.columns(2)

for index, skill in enumerate(skills):

    target_column = col1 if index % 2 == 0 else col2

    with target_column:

        default_values = {
            "Statistics": 65,
            "Python": 40,
            "SQL": 55,
            "Data Analysis": 60,
            "Data Visualization": 45
        }

        current_skills[skill] = st.slider(
            skill,
            min_value=0,
            max_value=100,
            value=default_values[skill],
            step=5
        )


# =========================================================
# ANALYZE BUTTON
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

_, button_col, _ = st.columns([1, 2, 1])

with button_col:

    analyze = st.button(
        "Analyze Competencies",
        type="primary"
    )


# =========================================================
# ANALYSIS RESULT
# =========================================================

if analyze:

    results = calculate_skill_gap(
        role,
        current_skills
    )

    if not results:

        st.error(
            "No competency framework found for the selected role."
        )

    else:

        st.markdown(
            '<div class="custom-divider"></div>',
            unsafe_allow_html=True
        )

        # -----------------------------------------------
        # OVERVIEW
        # -----------------------------------------------

        st.markdown(
            '<div class="section-title">Analysis Overview</div>',
            unsafe_allow_html=True
        )

        high_count = sum(
            r["priority"] == "High"
            for r in results
        )

        medium_count = sum(
            r["priority"] == "Medium"
            for r in results
        )

        low_count = sum(
            r["priority"] == "Low"
            for r in results
        )

        average_gap = round(
            sum(r["gap"] for r in results) / len(results)
        )


        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        Skills Assessed
                    </div>
                    <div class="metric-value">
                        {len(results)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with m2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        High Priority
                    </div>
                    <div class="metric-value">
                        {high_count}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with m3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        Medium Priority
                    </div>
                    <div class="metric-value">
                        {medium_count}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with m4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        Average Gap
                    </div>
                    <div class="metric-value">
                        {average_gap}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # -----------------------------------------------
        # DETAILS
        # -----------------------------------------------

        st.markdown(
            '<div class="section-title">Competency Gap Details</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="section-description">'
            f'Assessment for <b>{employee_name}</b> · {role}'
            f'</div>',
            unsafe_allow_html=True
        )


        for result in results:

            priority = result["priority"]

            if priority == "High":
                badge_class = "high"

            elif priority == "Medium":
                badge_class = "medium"

            else:
                badge_class = "low"


            current = result["current"]
            required = result["required"]
            gap = result["gap"]

            st.markdown(
                f"""
                <div class="result-card">

                    <div class="result-top">

                        <div>
                            <div class="result-name">
                                {result["skill"]}
                            </div>

                            <div class="result-info">
                                Current {current}% &nbsp;·&nbsp;
                                Required {required}%
                            </div>
                        </div>

                        <div>
                            <span class="{badge_class}">
                                {priority.upper()}
                            </span>
                        </div>

                    </div>

                    <div class="progress-background">

                        <div
                            class="progress-current"
                            style="width:{current}%;">
                        </div>

                    </div>

                    <div class="progress-labels">
                        <span>Current proficiency: {current}%</span>
                        <span>Skill gap: {gap}%</span>
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        # -----------------------------------------------
        # DEVELOPMENT FOCUS
        # -----------------------------------------------

        high_priority = [
            r for r in results
            if r["priority"] == "High"
        ]

        if high_priority:

            focus_skills = ", ".join(
                r["skill"] for r in high_priority
            )

            st.markdown(
                '<div class="section-title">'
                'Development Focus'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="focus-box">

                    <div class="focus-title">
                        Priority competency identified
                    </div>

                    <div class="focus-text">
                        <b>{focus_skills}</b> requires immediate
                        development based on the identified competency gap.
                        These skills should be prioritized in the
                        personalized learning pathway.
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )