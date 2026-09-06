import streamlit as st
from data import inject_custom_css, sidebar_profile_switcher, require_profile, get_recommendations, PRIORITY_COLORS, render_html

st.set_page_config(page_title="ATLAS | Recommendations", page_icon="🎯", layout="wide")
inject_custom_css()
sidebar_profile_switcher()
profile = require_profile()

st.title("🎯 Personalized Course Recommendations")
st.divider()

gap_rows = st.session_state.get("gap_rows")
if not gap_rows:
    st.info("Visit the Competency & Skill Gap page first to generate recommendations.")
    st.page_link("pages/2_Competency_Skill_Gap.py", label="Go to Skill Gap →", icon="📊")
    st.stop()

recs = get_recommendations(gap_rows)

if not recs:
    st.success("🎉 No significant skill gaps — this learner is up to date!")
else:
    st.caption(f"Showing {len(recs)} course(s) tailored to the current skill gaps.")
    for r in recs:
        color = PRIORITY_COLORS.get(r["priority"], "#6C6CFF")
        render_html(f"""
        <div class="atlas-card">
            <h4 style="margin-bottom:2px;">📘 {r['course']}
                <span class="atlas-badge" style="background:{color}; float:right;">{r['priority']} priority</span>
            </h4>
            <p style="color:#9BA0B4; margin-bottom:6px;">
                Targets: <b>{r['skill']}</b> &nbsp;•&nbsp; Level: {r['level']} &nbsp;•&nbsp; Duration: {r['duration']}
            </p>
            <p>{r['reason']}</p>
        </div>
        """)

st.divider()
st.page_link("pages/4_AI_Quiz.py", label="Next: Take AI Quiz →", icon="📝")
