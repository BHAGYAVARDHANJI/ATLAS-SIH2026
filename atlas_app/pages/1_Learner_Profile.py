import streamlit as st
from data import inject_custom_css, sidebar_profile_switcher, require_profile, require_login, render_html

st.set_page_config(page_title="ATLAS | Profile", page_icon="👤", layout="wide")
inject_custom_css()
require_login()
sidebar_profile_switcher()
profile = require_profile()

st.title("👤 Learner Profile")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    render_html(f"""
    <div class="atlas-card" style="text-align:center;">
        <div style="font-size:64px;">{profile['avatar']}</div>
        <h3>{profile['name']}</h3>
        <p style="color:#9BA0B4;">{profile['designation']}</p>
    </div>
    """)

with col2:
    render_html(f"""
    <div class="atlas-card">
        <div style="display:flex; gap:32px; flex-wrap:wrap;">
            <div style="flex:1; min-width:180px;">
                <p class="atlas-metric-label">Department</p>
                <p><b>{profile['department']}</b></p>
                <p class="atlas-metric-label">Role</p>
                <p><b>{profile['role']}</b></p>
            </div>
            <div style="flex:1; min-width:180px;">
                <p class="atlas-metric-label">Qualifications</p>
                <p><b>{profile['qualifications']}</b></p>
                <p class="atlas-metric-label">Experience</p>
                <p><b>{profile['experience']}</b></p>
            </div>
        </div>
    </div>
    """)

st.subheader("📚 Training History")
for t in profile["training_history"]:
    st.markdown(f"- {t}")

st.divider()
st.page_link("pages/2_Competency_Skill_Gap.py", label="Next: View Skill Gap →", icon="📊")