import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data import (
    inject_custom_css,
    sidebar_profile_switcher,
    get_profile,
    get_competency_profile,
    calculate_skill_gap,
    render_html,
)

st.set_page_config(
    page_title="ATLAS | Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# SETUP
# ---------------------------------------------------------
inject_custom_css()
sidebar_profile_switcher()

profile = get_profile(st.session_state.selected_profile)

competencies = get_competency_profile(profile["id"])
gap_rows = calculate_skill_gap(competencies) if competencies else []
df = pd.DataFrame(gap_rows)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------
first_name = profile["name"].split()[0]

render_html(f"""
<div class="atlas-hero">
    <span class="atlas-eyebrow">ATLAS • ADAPTIVE TRAINING &amp; LEARNING ASSISTANCE SYSTEM</span>
    <div class="atlas-hero-title">{profile['avatar']} Welcome back, {first_name} 👋</div>
    <div class="atlas-hero-sub">
        Your personalized learning intelligence dashboard for
        <b style="color:#F5F6FA;">{profile['role']}</b>.
    </div>
</div>
""")


# ---------------------------------------------------------
# EMPTY STATE
# ---------------------------------------------------------
if not competencies or df.empty:
    st.info(
        "No competency data is available for this learner yet. "
        "Please select a profile with competency mapping."
    )
    st.stop()


# ---------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------
total_skills = len(df)

high_priority = int((df["priority"] == "High").sum())
medium_priority = int((df["priority"] == "Medium").sum())
low_priority = int((df["priority"] == "Low").sum())

avg_current = safe_average(df["current"])
avg_required = safe_average(df["required"])
avg_gap = safe_average(df["gap"])

max_scale = 100 if df[["current", "required"]].to_numpy().max() > 5 else 5

readiness = round((avg_current / avg_required) * 100, 1) if avg_required else 0
readiness = min(readiness, 100)

top_gap = df.loc[df["gap"].idxmax()]
strongest_skill = df.loc[df["current"].idxmax()]


# ---------------------------------------------------------
# KEY METRICS
# ---------------------------------------------------------
st.markdown("### 📊 Learner Overview")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "🎯 Skill Readiness",
        f"{readiness:.0f}%",
        help="Current average competency compared with the required average.",
    )

with m2:
    st.metric("📚 Skills Tracked", total_skills)

with m3:
    st.metric("🔴 High Priority", high_priority)

with m4:
    st.metric(
        "📉 Average Gap",
        f"{avg_gap:.1f}" if max_scale == 5 else f"{avg_gap:.0f}",
    )

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# READINESS + PRIORITY
# ---------------------------------------------------------
left, right = st.columns([1.25, 1])

with left:
    st.markdown("### 🚀 Competency Readiness")

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=readiness,
            number={"suffix": "%", "font": {"size": 42, "color": "#F5F6FA"}},
            title={"text": "Overall Skill Readiness", "font": {"size": 18, "color": "#9BA0B4"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#737B8C"},
                "bar": {"color": "#6C6CFF"},
                "bgcolor": "#1B2033",
                "borderwidth": 0,
            },
        )
    )

    fig.update_layout(
        height=280,
        margin=dict(l=25, r=25, t=45, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#F5F6FA",
    )

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with right:
    st.markdown("### 🚦 Gap Priority")

    priority_df = pd.DataFrame({
        "Priority": ["High", "Medium", "Low"],
        "Skills": [high_priority, medium_priority, low_priority],
    })

    fig = go.Figure(
        go.Bar(
            x=priority_df["Skills"],
            y=priority_df["Priority"],
            orientation="h",
            text=priority_df["Skills"],
            textposition="outside",
            marker_color=["#FF5C7A", "#FFB454", "#37D6A0"],
        )
    )

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=45, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#F5F6FA",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        showlegend=False,
    )

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ---------------------------------------------------------
# DEVELOPMENT ALERT
# ---------------------------------------------------------
st.markdown("### ⚡ Development Alert")

render_html(f"""
<div class="atlas-card" style="border-left:4px solid #FF5C7A;">
    <div class="atlas-metric-label">HIGHEST DEVELOPMENT PRIORITY</div>
    <div style="font-size:1.35rem; font-weight:700; color:#F5F6FA; margin-top:5px; font-family:'Sora', sans-serif;">
        {top_gap['competency']}
    </div>
    <div style="color:#9BA0B4; margin-top:8px;">
        Current level: <b style="color:#F5F6FA;">{top_gap['current']}</b>
        &nbsp; → &nbsp;
        Required: <b style="color:#F5F6FA;">{top_gap['required']}</b>
        &nbsp; • &nbsp;
        Gap: <b style="color:#FF5C7A;">{top_gap['gap']}</b>
    </div>
</div>
""")

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SKILL SNAPSHOT
# ---------------------------------------------------------
st.markdown("### 🧠 Skill Snapshot")

snapshot_left, snapshot_right = st.columns([1.3, 1])

with snapshot_left:
    categories = df["competency"].tolist()

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=df["current"].tolist() + [df["current"].iloc[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Current",
            line=dict(color="#6C6CFF", width=3),
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=df["required"].tolist() + [df["required"].iloc[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Required",
            line=dict(color="#37D6C4", width=2),
            opacity=0.45,
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max_scale], gridcolor="#2A3047", tickfont=dict(color="#9BA0B4")),
            angularaxis=dict(gridcolor="#2A3047", tickfont=dict(color="#9BA0B4")),
        ),
        height=430,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#F5F6FA",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with snapshot_right:
    st.markdown("#### 🏆 Current Strength")

    render_html(f"""
    <div class="atlas-card">
        <div class="atlas-metric-label">STRONGEST COMPETENCY</div>
        <div style="font-size:1.3rem; font-weight:700; margin-top:8px; font-family:'Sora', sans-serif;">
            {strongest_skill['competency']}
        </div>
        <div style="color:#9BA0B4; margin-top:8px;">Current level</div>
        <div style="font-size:1.8rem; font-weight:800; color:#37D6A0; font-family:'Sora', sans-serif;">
            {strongest_skill['current']}
        </div>
    </div>
    """)

    st.markdown("#### 📌 Biggest Gaps")

    biggest_gaps = df.sort_values("gap", ascending=False).head(4)

    for _, row in biggest_gaps.iterrows():
        status = skill_status(row["gap"])
        render_html(f"""
        <div style="padding:12px 14px; margin-bottom:9px; border-radius:12px; background:var(--atlas-surface); border:1px solid var(--atlas-border);">
            <div style="display:flex; justify-content:space-between; gap:10px;">
                <b>{row['competency']}</b>
                <span style="color:#FF5C7A; font-weight:700;">Gap {row['gap']}</span>
            </div>
            <div style="margin-top:5px; color:#9BA0B4; font-size:0.85rem;">
                {status} • Current {row['current']} / Required {row['required']}
            </div>
        </div>
        """)


# ---------------------------------------------------------
# LEARNING JOURNEY
# ---------------------------------------------------------
st.markdown("### 🧭 Your ATLAS Learning Journey")

journey = [
    ("01", "Learner Profile", "Understand your role, qualifications and training history."),
    ("02", "Skill Gap Analysis", "Identify the difference between current and required competencies."),
    ("03", "Personalized Recommendations", "Discover learning resources targeted to your biggest gaps."),
    ("04", "AI Quiz", "Validate your understanding and identify weak areas."),
    ("05", "Progress Tracking", "Measure improvement and continuously refine your learning path."),
]

for number, title, description in journey:
    render_html(f"""
    <div class="atlas-row">
        <div class="atlas-row-index">{number}</div>
        <div>
            <div style="font-weight:700; font-size:1rem;">{title}</div>
            <div style="color:#9BA0B4; font-size:0.88rem; margin-top:3px;">{description}</div>
        </div>
    </div>
    """)


# ---------------------------------------------------------
# QUICK ACTIONS
# ---------------------------------------------------------
st.markdown("### ⚡ Quick Actions")

q1, q2, q3 = st.columns(3)

with q1:
    st.page_link("pages/1_Learner_Profile.py", label="👤 View Learner Profile", width="stretch")

with q2:
    st.page_link("pages/2_Competency_Skill_Gap.py", label="📊 Analyze Skill Gap", width="stretch")

with q3:
    st.page_link("pages/3_Recommendations.py", label="🎯 Get Recommendations", width="stretch")

q4, q5 = st.columns(2)

with q4:
    st.page_link("pages/4_AI_Quiz.py", label="📝 Start AI Quiz", width="stretch")

with q5:
    st.page_link("pages/5_Progress.py", label="📈 Track Progress", width="stretch")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()

st.caption(
    f"ATLAS • Personalized learning intelligence for {profile['role']} • "
    "Adaptive Training & Learning Assistance System"
)