import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import db
import auth
from data import (
    inject_custom_css,
    sidebar_profile_switcher,
    theme_toggle_control,
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

db.init_db()
db.seed_demo_data()
db.seed_demo_users()
inject_custom_css()

# ---------------------------------------------------------
# LOGIN / SIGNUP
# ---------------------------------------------------------
if not auth.is_authenticated():
    st.sidebar.markdown("### 🎓 ATLAS")
    st.sidebar.caption("Smart Education Platform")
    theme_toggle_control(st.sidebar)

    render_html("""
    <div class="atlas-hero">
        <span class="atlas-eyebrow">ATLAS • ADAPTIVE TRAINING &amp; LEARNING ASSISTANCE SYSTEM</span>
        <div class="atlas-hero-title">🎓 Welcome to ATLAS</div>
        <div class="atlas-hero-sub">Log in or create an account to continue.</div>
    </div>
    """)

    login_tab, signup_tab = st.tabs(["🔑 Log In", "🆕 Sign Up"])

    with login_tab:
        st.caption("Demo accounts: **ananya / atlas123**, **rohit / atlas123**, **rahul / atlas123**")
        with st.form("login_form"):
            login_username = st.text_input("Username")
            login_password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button(
                "Log In", type="primary", width="stretch"
            )

        if login_submitted:
            success, message = auth.login(login_username, login_password)
            if success:
                st.rerun()
            else:
                st.error(message)

    with signup_tab:
        profile_options = db.get_all_profile_codes()
        profile_map = {code: db.get_profile(code) for code in profile_options}
        available_profiles = [
            code for code in profile_options if db.get_user_by_profile(code) is None
        ]

        with st.form("signup_form"):
            signup_username = st.text_input("Choose a username")
            signup_profile = st.selectbox(
                "Link this account to learner",
                options=available_profiles,
                format_func=lambda code: f"{profile_map[code]['avatar']} {profile_map[code]['name']}",
            ) if available_profiles else None
            signup_password = st.text_input("Choose a password", type="password")
            signup_password_confirm = st.text_input("Confirm password", type="password")
            signup_submitted = st.form_submit_button(
                "Create Account", type="primary", width="stretch"
            )

        if signup_submitted:
            if not available_profiles:
                st.error("All demo learner profiles are already linked to accounts.")
            elif signup_password != signup_password_confirm:
                st.error("Passwords do not match.")
            else:
                success, message = auth.signup(
                    signup_username, signup_password, signup_profile
                )
                if success:
                    st.success(message + " Switch to the Log In tab above.")
                else:
                    st.error(message)

    st.stop()

# ---------------------------------------------------------
# LOGGED-IN DASHBOARD
# ---------------------------------------------------------
sidebar_profile_switcher()
profile = get_profile(auth.current_profile_id())

competencies = get_competency_profile(profile["id"])
gap_rows = calculate_skill_gap(competencies) if competencies else []
df = pd.DataFrame(gap_rows)


def safe_average(values):
    values = list(values)
    return round(sum(values) / len(values), 1) if values else 0


def skill_status(gap):
    if gap <= 0:
        return "Ready"
    elif gap <= 1:
        return "Developing"
    return "Needs Focus"


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

if not competencies or df.empty:
    st.info("No competency data is available for this learner yet.")
    st.stop()

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

st.markdown("### 📊 Learner Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("🎯 Skill Readiness", f"{readiness:.0f}%")
m2.metric("📚 Skills Tracked", total_skills)
m3.metric("🔴 High Priority", high_priority)
m4.metric("📉 Average Gap", f"{avg_gap:.1f}" if max_scale == 5 else f"{avg_gap:.0f}")

left, right = st.columns([1.25, 1])
with left:
    st.markdown("### 🚀 Competency Readiness")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=readiness,
        number={"suffix": "%", "font": {"size": 42, "color": "#F5F6FA"}},
        title={"text": "Overall Skill Readiness", "font": {"size": 18, "color": "#9BA0B4"}},
        gauge={"axis": {"range": [0, 100], "tickcolor": "#737B8C"}, "bar": {"color": "#6C6CFF"}, "bgcolor": "#1B2033", "borderwidth": 0},
    ))
    fig.update_layout(height=280, margin=dict(l=25, r=25, t=45, b=10), paper_bgcolor="rgba(0,0,0,0)", font_color="#F5F6FA")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with right:
    st.markdown("### 🚦 Gap Priority")
    priority_df = pd.DataFrame({"Priority": ["High", "Medium", "Low"], "Skills": [high_priority, medium_priority, low_priority]})
    fig = go.Figure(go.Bar(x=priority_df["Skills"], y=priority_df["Priority"], orientation="h", text=priority_df["Skills"], textposition="outside", marker_color=["#FF5C7A", "#FFB454", "#37D6A0"]))
    fig.update_layout(height=280, margin=dict(l=20, r=45, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F5F6FA", xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=False), showlegend=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

st.markdown("### ⚡ Development Alert")
render_html(f"""
<div class="atlas-card" style="border-left:4px solid #FF5C7A;">
    <div class="atlas-metric-label">HIGHEST DEVELOPMENT PRIORITY</div>
    <div style="font-size:1.35rem; font-weight:700; color:#F5F6FA; margin-top:5px; font-family:'Sora', sans-serif;">{top_gap['competency']}</div>
    <div style="color:#9BA0B4; margin-top:8px;">Current level: <b style="color:#F5F6FA;">{top_gap['current']}</b> &nbsp; → &nbsp; Required: <b style="color:#F5F6FA;">{top_gap['required']}</b> &nbsp; • &nbsp; Gap: <b style="color:#FF5C7A;">{top_gap['gap']}</b></div>
</div>
""")

st.markdown("### 🧠 Skill Snapshot")
snapshot_left, snapshot_right = st.columns([1.3, 1])
with snapshot_left:
    categories = df["competency"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=df["current"].tolist() + [df["current"].iloc[0]], theta=categories + [categories[0]], fill="toself", name="Current", line=dict(color="#6C6CFF", width=3)))
    fig.add_trace(go.Scatterpolar(r=df["required"].tolist() + [df["required"].iloc[0]], theta=categories + [categories[0]], fill="toself", name="Required", line=dict(color="#37D6C4", width=2), opacity=0.45))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max_scale], gridcolor="#2A3047", tickfont=dict(color="#9BA0B4")), angularaxis=dict(gridcolor="#2A3047", tickfont=dict(color="#9BA0B4"))), height=430, margin=dict(l=40, r=40, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", font_color="#F5F6FA")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
with snapshot_right:
    st.markdown("#### 🏆 Current Strength")
    render_html(f"""
    <div class="atlas-card">
        <div class="atlas-metric-label">STRONGEST COMPETENCY</div>
        <div style="font-size:1.3rem; font-weight:700; margin-top:8px; font-family:'Sora', sans-serif;">{strongest_skill['competency']}</div>
        <div style="color:#9BA0B4; margin-top:8px;">Current level</div>
        <div style="font-size:1.8rem; font-weight:800; color:#37D6A0; font-family:'Sora', sans-serif;">{strongest_skill['current']}</div>
    </div>
    """)

journey_steps = ["Learner Profile", "Skill Gap Analysis", "Recommendations", "AI Quiz", "Progress Tracking"]
steps_html = "".join(
    f'<div class="atlas-step"><span class="atlas-step-dot">{i+1}</span><span>{name}</span></div>'
    + ('<div class="atlas-step-line"></div>' if i < len(journey_steps) - 1 else '')
    for i, name in enumerate(journey_steps)
)
render_html(f'<div class="atlas-step-track">{steps_html}</div>')

st.markdown("### ⚡ Quick Actions")
q1, q2, q3 = st.columns(3)
with q1:
    if st.button("👤 View Learner Profile", width="stretch"):
        st.switch_page("pages/1_Learner_Profile.py")
with q2:
    if st.button("📊 Analyze Skill Gap", width="stretch"):
        st.switch_page("pages/2_Competency_Skill_Gap.py")
with q3:
    if st.button("🎯 Get Recommendations", width="stretch"):
        st.switch_page("pages/3_Recommendations.py")
q4, q5 = st.columns(2)
with q4:
    if st.button("📝 Start AI Quiz", width="stretch"):
        st.switch_page("pages/4_AI_Quiz.py")
with q5:
    if st.button("📈 Track Progress", width="stretch"):
        st.switch_page("pages/5_Progress.py")

st.divider()
st.caption(f"ATLAS • Personalized learning intelligence for {profile['role']} • Adaptive Training & Learning Assistance System")
