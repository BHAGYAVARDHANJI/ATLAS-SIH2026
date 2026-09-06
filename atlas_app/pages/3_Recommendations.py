import streamlit as st
from data import inject_custom_css, sidebar_profile_switcher, require_profile, get_recommendations, PRIORITY_COLORS

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

if not recs:
    st.success("🎉 No significant skill gaps — this learner is up to date!")
else:
    st.caption(f"Showing {len(recs)} course(s) tailored to the current skill gaps.")
    for r in recs:
        color = PRIORITY_COLORS.get(r["priority"], "#4F8BF9")
        st.markdown(f"""
            <div class="atlas-card">
                <h4 style="margin-bottom:2px;">📘 {r['course']}
                    <span class="atlas-badge" style="background:{color}; float:right;">{r['priority']} priority</span>
                </h4>
                <p style="color:#9BA3AF; margin-bottom:6px;">
                    Targets: <b>{r['skill']}</b> &nbsp;•&nbsp; Level: {r['level']} &nbsp;•&nbsp; Duration: {r['duration']}
                </p>
                <p>{r['reason']}</p>
            </div>
        """, unsafe_allow_html=True)

st.divider()
st.page_link("pages/4_AI_Quiz.py", label="Next: Take the AI Quiz →", icon="📝")