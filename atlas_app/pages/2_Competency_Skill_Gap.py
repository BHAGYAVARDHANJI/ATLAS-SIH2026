import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data import (
    inject_custom_css, sidebar_profile_switcher, require_profile,
    get_competency_profile, calculate_skill_gap, PRIORITY_COLORS,
)

st.set_page_config(page_title="ATLAS | Skill Gap", page_icon="📊", layout="wide")
inject_custom_css()
sidebar_profile_switcher()
profile = require_profile()

st.title("📊 Competency & Skill Gap")
st.caption(f"Role: **{profile['role']}**")
st.divider()

competencies = get_competency_profile(profile["role"])

if not competencies:
    st.warning("No competency mapping found for this role yet.")
    st.stop()

gap_rows = calculate_skill_gap(competencies)
st.session_state.gap_rows = gap_rows  # hand off to Recommendations page
df = pd.DataFrame(gap_rows)

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Current vs Required Levels")
    categories = df["competency"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=df["current"].tolist() + [df["current"].tolist()[0]],
        theta=categories + [categories[0]],
        fill="toself", name="Current Level", line_color="#4F8BF9",
    ))
    fig.add_trace(go.Scatterpolar(
        r=df["required"].tolist() + [df["required"].tolist()[0]],
        theta=categories + [categories[0]],
        fill="toself", name="Required Level", line_color="#FF4B4B", opacity=0.5,
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        margin=dict(l=40, r=40, t=20, b=20),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Gap Breakdown")
    for row in gap_rows:
        color = PRIORITY_COLORS[row["priority"]]
        st.markdown(f"""
            <div class="atlas-card">
                <b>{row['competency']}</b>
                <span class="atlas-badge" style="background:{color};float:right;">{row['priority']}</span>
                <br>
                <span style="color:#9BA3AF;">Current: {row['current']} / Required: {row['required']}</span>
                <br>
                <progress value="{row['current']}" max="{row['required']}" style="width:100%; accent-color:{color};"></progress>
            </div>
        """, unsafe_allow_html=True)

st.divider()
st.page_link("pages/3_Recommendations.py", label="Next: See Recommendations →", icon="🎯")
