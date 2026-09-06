import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import (
    inject_custom_css,
    sidebar_profile_switcher,
    require_profile,
    require_login,
    get_competency_profile,
    calculate_skill_gap,
    PRIORITY_COLORS,
    render_html,
)
from chatbot import render_chatbot

st.set_page_config(page_title="ATLAS | Skill Gap", page_icon="📊", layout="wide")
inject_custom_css()
require_login()
sidebar_profile_switcher()
profile = require_profile()

st.title("📊 Competency & Skill Gap Analysis")
st.divider()

# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------
competencies = get_competency_profile(profile["id"])
gap_rows = calculate_skill_gap(competencies) if competencies else []
df = pd.DataFrame(gap_rows)

if not competencies or df.empty:
    st.info(
        "No competency data is available for this learner yet. "
        "Please select a profile with competency mapping."
    )
    st.stop()

# Make the gap data available to other pages (Recommendations, AI Coach, etc.)
st.session_state.gap_rows = gap_rows


def safe_average(values):
    values = list(values)
    return round(sum(values) / len(values), 1) if values else 0


def skill_status(gap):
    if gap <= 0:
        return "Ready"
    elif gap <= 1:
        return "Developing"
    else:
        return "Needs Focus"


def priority_badge(priority):
    css_class = {
        "High": "atlas-badge-high",
        "Medium": "atlas-badge-medium",
        "Low": "atlas-badge-low",
        "None": "atlas-badge-none",
    }.get(priority, "atlas-badge-low")
    return f'<span class="atlas-badge {css_class}">{priority}</span>'


# ---------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------
total_skills = len(df)
high_count = int((df["priority"] == "High").sum())
medium_count = int((df["priority"] == "Medium").sum())
low_count = int((df["priority"] == "Low").sum())
ready_count = int((df["priority"] == "None").sum())

avg_current = safe_average(df["current"])
avg_required = safe_average(df["required"])
avg_gap = safe_average(df["gap"])

max_scale = 100 if df[["current", "required"]].to_numpy().max() > 5 else 5
top_row = df.loc[df["gap"].idxmax()]

# ---------------------------------------------------------
# KEY METRICS
# ---------------------------------------------------------
st.markdown("### 📈 Skill Gap Overview")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("📚 Total Skills", total_skills)
with m2:
    st.metric("🔴 High Priority", high_count)
with m3:
    st.metric("🟡 Medium Priority", medium_count)
with m4:
    st.metric("📉 Average Gap", f"{avg_gap:.1f}" if max_scale == 5 else f"{avg_gap:.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# CURRENT VS REQUIRED CHART
# ---------------------------------------------------------
left, right = st.columns([1.4, 1])

with left:
    st.markdown("### 📊 Current vs Required Levels")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Current",
        x=df["competency"],
        y=df["current"],
        marker_color="#6C6CFF",
    ))
    fig.add_trace(go.Bar(
        name="Required",
        x=df["competency"],
        y=df["required"],
        marker_color="#37D6C4",
        opacity=0.55,
    ))
    fig.update_layout(
        barmode="group",
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#F5F6FA",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#2A3047"),
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with right:
    st.markdown("### 🚦 Priority Breakdown")

    priority_df = pd.DataFrame({
        "Priority": ["High", "Medium", "Low", "Ready"],
        "Skills": [high_count, medium_count, low_count, ready_count],
    })
    fig = go.Figure(go.Pie(
        labels=priority_df["Priority"],
        values=priority_df["Skills"],
        hole=0.55,
        marker=dict(colors=["#FF5C7A", "#FFB454", "#6C6CFF", "#37D6A0"]),
        textfont=dict(color="#F5F6FA"),
    ))
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#F5F6FA",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

# ---------------------------------------------------------
# DETAILED TABLE
# ---------------------------------------------------------
st.markdown("### 🧾 Detailed Skill Gap Table")

for _, row in df.sort_values("gap", ascending=False).iterrows():
    status = skill_status(row["gap"])
    render_html(f"""
    <div class="atlas-card" style="padding:16px 20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
            <div>
                <b style="font-size:1.05rem;">{row['competency']}</b>
                <div style="color:#9BA0B4; font-size:0.85rem; margin-top:2px;">
                    {status} • Current {row['current']} / Required {row['required']} • Gap {row['gap']}
                </div>
            </div>
            {priority_badge(row['priority'])}
        </div>
    </div>
    """)

st.divider()
st.page_link("pages/3_Recommendations.py", label="Next: Get Recommendations →", icon="🎯")

# =========================================================
# ATLAS AI COACH (free, rule-based — no external API needed)
# =========================================================
st.divider()
render_chatbot(profile=profile, gap_rows=gap_rows)