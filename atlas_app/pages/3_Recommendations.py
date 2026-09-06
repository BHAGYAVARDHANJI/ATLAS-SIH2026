import streamlit as st
from data import (
    inject_custom_css, sidebar_profile_switcher, require_profile,
    get_recommendations, PRIORITY_COLORS,
)

st.set_page_config(page_title="ATLAS | Recommendations", page_icon="🎯", layout="wide")
inject_custom_css()
sidebar_profile_switcher()
profile = require_profile()

st.title("🎯 Personalized Course Recommendations")
st.caption(f"Learner: **{profile['name']}**  •  Role: **{profile['role']}**")
st.divider()

gap_rows = st.session_state.get("gap_rows")

if not gap_rows:
    st.warning("⚠️ No skill-gap data found yet. Visit the Skill Gap page first.")
    st.page_link("pages/2_Competency_Skill_Gap.py", label="Go to Skill Gap →", icon="📊")
    st.stop()

recommendations = get_recommendations(gap_rows)

if not recommendations:
    st.success("🎉 No skill gaps found — this learner already meets all required competency levels!")
    st.stop()

st.subheader(f"Top {len(recommendations)} Recommended Courses")

for rec in recommendations:
    color = PRIORITY_COLORS.get(rec["priority"], "#4F8BF9")
    st.markdown(f"""
        <div class="atlas-card">
            <b>{rec['course']}</b>
            <span class="atlas-badge" style="background:{color};float:right;">{rec['priority']} Priority</span>
            <br>
            <span style="color:#9BA3AF;">Skill: {rec['skill']} • Level: {rec['level']} • Duration: {rec['duration']}</span>
            <br><br>
            <span style="color:#FAFAFA;">💡 <i>Why recommended:</i> {rec['reason']}</span>
        </div>
    """, unsafe_allow_html=True)

st.divider()
st.page_link("pages/4_AI_Quiz.py", label="Next: Take the AI Quiz →", icon="📝")