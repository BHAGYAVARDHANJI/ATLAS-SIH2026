import streamlit as st
from data import inject_custom_css, sidebar_profile_switcher, require_profile

st.set_page_config(page_title="ATLAS | Profile", page_icon="👤", layout="wide")
inject_custom_css()
sidebar_profile_switcher()
profile = require_profile()

st.title("👤 Learner Profile")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"""
        <div class="atlas-card" style="text-align:center;">
        <div style="font-size:64px;">{profile['avatar']}</div>
        <h3>{profile['name']}</h3>
        <p style="color:#9BA3AF;">{profile['designation']}</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="atlas-card">', unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        st.markdown('<p class="atlas-metric-label">Department</p>', unsafe_allow_html=True)
        st.write(f"**{profile['department']}**")
        st.markdown('<p class="atlas-metric-label">Role</p>', unsafe_allow_html=True)
        st.write(f"**{profile['role']}**")
    with b:
        st.markdown('<p class="atlas-metric-label">Qualifications</p>', unsafe_allow_html=True)
        st.write(f"**{profile['qualifications']}**")
        st.markdown('<p class="atlas-metric-label">Experience</p>', unsafe_allow_html=True)
        st.write(f"**{profile['experience']}**")
    st.markdown('</div>', unsafe_allow_html=True)

st.subheader("📚 Training History")
for t in profile["training_history"]:
    st.markdown(f"- {t}")

st.divider()
st.page_link("pages/2_Competency_Skill_Gap.py", label="Next: View Skill Gap →", icon="📊")
