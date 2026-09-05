import streamlit as st
from data import inject_custom_css, sidebar_profile_switcher, get_profile, get_competency_profile, calculate_skill_gap

st.set_page_config(page_title="ATLAS | Home", page_icon="🎓", layout="wide")
inject_custom_css()
sidebar_profile_switcher()

profile = get_profile(st.session_state.selected_profile)

# ---------- HERO ----------
st.markdown(f"## {profile['avatar']} Welcome back, {profile['name'].split()[0]} 👋")
st.caption("ATLAS — Adaptive Training & Learning Assistance System")
st.divider()

# ---------- QUICK STATS ----------
competencies = get_competency_profile(profile["role"])
gap_rows = calculate_skill_gap(competencies) if competencies else []
high_priority = [g for g in gap_rows if g["priority"] == "High"]
avg_gap = round(sum(g["gap"] for g in gap_rows) / len(gap_rows), 1) if gap_rows else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Role", profile["role"])
c2.metric("Competencies Tracked", len(competencies))
c3.metric("High-Priority Gaps", len(high_priority), delta=None)
c4.metric("Avg Skill Gap", avg_gap)

st.divider()

# ---------- NAVIGATION CARDS ----------
st.markdown("### Where to next?")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="atlas-card">
        <h4>👤 Learner Profile</h4>
        <p style="color:#9BA3AF;">View designation, department, qualifications & training history.</p>
        </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Learner_Profile.py", label="Open Profile →", icon="👤")

with col2:
    st.markdown("""
        <div class="atlas-card">
        <h4>📊 Skill Gap</h4>
        <p style="color:#9BA3AF;">See current vs required competency levels with priority flags.</p>
        </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Competency_Skill_Gap.py", label="View Skill Gap →", icon="📊")

with col3:
    st.markdown("""
        <div class="atlas-card">
        <h4>🎯 Recommendations</h4>
        <p style="color:#9BA3AF;">Get personalized iGOT courses that close your biggest gaps.</p>
        </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_Recommendations.py", label="See Courses →", icon="🎯")

col4, col5 = st.columns(2)
with col4:
    st.markdown("""
        <div class="atlas-card">
        <h4>📝 AI Quiz</h4>
        <p style="color:#9BA3AF;">Test your knowledge with an adaptive AI-generated quiz.</p>
        </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_AI_Quiz.py", label="Start Quiz →", icon="📝")

with col5:
    st.markdown("""
        <div class="atlas-card">
        <h4>📈 Progress</h4>
        <p style="color:#9BA3AF;">Track scores and improvement over time.</p>
        </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/5_Progress.py", label="View Progress →", icon="📈")
