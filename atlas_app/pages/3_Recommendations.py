import pandas as pd
import streamlit as st

from data import (
    inject_custom_css,
    sidebar_profile_switcher,
    require_profile,
    require_login,
    get_competency_profile,
    calculate_skill_gap,
    get_recommendations,
    render_html,
)
from chatbot import render_chatbot

st.set_page_config(
    page_title="ATLAS | Recommendations",
    page_icon="🎯",
    layout="wide",
)

inject_custom_css()
require_login()
sidebar_profile_switcher()
profile = require_profile()

st.title("🎯 Personalized Learning Recommendations")
st.divider()

# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------
competencies = get_competency_profile(profile["id"])
gap_rows = calculate_skill_gap(competencies) if competencies else []

if not gap_rows:
    st.info(
        "No competency data is available for this learner yet. "
        "Please select a profile with competency mapping."
    )
    st.stop()

# Keep the current learner's gap data available to the coach.
st.session_state.gap_rows = gap_rows

recommendations = get_recommendations(gap_rows)

# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------
gaps = [r for r in gap_rows if r["gap"] > 0]
high = sum(r["priority"] == "High" for r in gaps)
medium = sum(r["priority"] == "Medium" for r in gaps)
low = sum(r["priority"] == "Low" for r in gaps)

st.markdown("### 📚 Learning Plan")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Skills Needing Development", len(gaps))
m2.metric("High Priority", high)
m3.metric("Medium Priority", medium)
m4.metric("Courses Found", len(recommendations))

# ---------------------------------------------------------
# NO RECOMMENDATIONS
# ---------------------------------------------------------
if not recommendations:
    st.success(
        "🎉 No learning recommendations are needed right now. "
        "All mapped competencies are at or above their required levels."
    )
else:
    st.markdown("### 🎯 Recommended Learning Resources")
    st.caption(
        f"Personalized for {profile['name']} based on the learner's current "
        "competency gaps. Larger gaps are shown first."
    )

    for rec in recommendations:
        priority = rec["priority"]
        if priority == "High":
            badge = "🔴 HIGH"
        elif priority == "Medium":
            badge = "🟡 MEDIUM"
        else:
            badge = "🔵 LOW"

        render_html(f"""
        <div class="atlas-card">
            <div style="display:flex; justify-content:space-between; gap:16px; align-items:flex-start; flex-wrap:wrap;">
                <div style="flex:1; min-width:260px;">
                    <div style="font-size:1.15rem; font-weight:700; font-family:'Sora', sans-serif;">
                        {rec['course']}
                    </div>
                    <div style="color:#9BA0B4; margin-top:6px;">
                        {rec['description']}
                    </div>
                </div>
                <div style="font-weight:700;">{badge}</div>
            </div>

            <div style="display:flex; gap:24px; flex-wrap:wrap; margin-top:16px; color:#9BA0B4; font-size:0.9rem;">
                <span>📌 Skill: <b style="color:#F5F6FA;">{rec['skill']}</b></span>
                <span>📈 Level: <b style="color:#F5F6FA;">{rec['level']}</b></span>
                <span>⏱️ Duration: <b style="color:#F5F6FA;">{rec['duration']}</b></span>
            </div>

            <div style="margin-top:14px; color:#9BA0B4; font-size:0.88rem;">
                💡 {rec['reason']}
            </div>
        </div>
        """)

# ---------------------------------------------------------
# NEXT STEP
# ---------------------------------------------------------
st.divider()

if st.button("📝 Next: Take AI Quiz →", type="primary", width="stretch"):
    st.switch_page("pages/4_AI_Quiz.py")

# ---------------------------------------------------------
# ATLAS AI COACH
# ---------------------------------------------------------
st.divider()
render_chatbot(profile=profile, gap_rows=gap_rows)
