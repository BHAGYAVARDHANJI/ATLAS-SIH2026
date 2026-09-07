import pandas as pd
import plotly.express as px
import streamlit as st

from data import (
    inject_custom_css,
    sidebar_profile_switcher,
    require_login,
    require_profile,
    get_progress_log,
)

st.set_page_config(
    page_title="ATLAS | Progress",
    page_icon="📈",
    layout="wide",
)

inject_custom_css()
require_login()
sidebar_profile_switcher()
profile = require_profile()

st.title("📈 Progress Dashboard")
st.divider()

# ------------------------------------------------------------
# READ PERSISTED PROGRESS FOR THE ACTIVE LEARNER
# ------------------------------------------------------------
profile_id = profile["id"]
log = get_progress_log(profile_id)

# ------------------------------------------------------------
# NO ATTEMPTS
# ------------------------------------------------------------
if not log:
    st.info(
        "No quiz attempts yet. Complete and submit a quiz to see "
        "your progress here."
    )
    st.page_link(
        "pages/4_AI_Quiz.py",
        label="Take a Quiz →",
        icon="📝",
    )
    st.stop()

# ------------------------------------------------------------
# PREPARE DATA
# ------------------------------------------------------------
df = pd.DataFrame(log)

required_columns = {"score", "total_questions"}
if not required_columns.issubset(df.columns):
    st.error("Progress data is incomplete. Please submit a new quiz.")
    st.stop()

df = df.rename(columns={"total_questions": "total"})

df["score"] = pd.to_numeric(df["score"], errors="coerce")
df["total"] = pd.to_numeric(df["total"], errors="coerce")

df = df[
    df["total"].notna()
    & (df["total"] > 0)
    & df["score"].notna()
    & (df["score"] >= 0)
    & (df["score"] <= df["total"])
].copy()

if df.empty:
    st.info(
        "No valid quiz attempts yet. Complete and submit a quiz "
        "to see progress here."
    )
    st.page_link(
        "pages/4_AI_Quiz.py",
        label="Take a Quiz →",
        icon="📝",
    )
    st.stop()

# Oldest -> newest, matching the database query order.
if "attempted_at" in df.columns:
    df["attempted_at"] = pd.to_datetime(
        df["attempted_at"],
        errors="coerce",
    )
    df = df.sort_values(
        ["attempted_at", "id"] if "id" in df.columns else ["attempted_at"],
        kind="stable",
    )

df = df.reset_index(drop=True)
df["percent"] = (df["score"] / df["total"] * 100).round(1)
df["attempt"] = range(1, len(df) + 1)

# ------------------------------------------------------------
# DASHBOARD METRICS
# ------------------------------------------------------------
c1, c2, c3 = st.columns(3)

latest = df.iloc[-1]

c1.metric(
    "Attempts",
    len(df),
)

c2.metric(
    "Latest Score",
    f"{int(latest['score'])}/{int(latest['total'])}",
    f"{latest['percent']}%",
)

c3.metric(
    "Best Score",
    f"{df['percent'].max():.1f}%",
)

# ------------------------------------------------------------
# SCORE TREND
# ------------------------------------------------------------
st.subheader("Score Trend")

fig = px.line(
    df,
    x="attempt",
    y="percent",
    markers=True,
    labels={
        "attempt": "Attempt #",
        "percent": "Score (%)",
    },
)

fig.update_traces(
    line_color="#4F8BF9",
    marker=dict(size=9),
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#FAFAFA",
    height=380,
    yaxis_range=[0, 100],
)

st.plotly_chart(
    fig,
    width="stretch",
)

# ------------------------------------------------------------
# ATTEMPT LOG
# ------------------------------------------------------------
st.subheader("Attempt Log")

display_columns = ["attempt", "score", "total", "percent"]
st.dataframe(
    df[display_columns],
    width="stretch",
    hide_index=True,
)

st.divider()
st.page_link(
    "pages/4_AI_Quiz.py",
    label="Take Another Quiz →",
    icon="📝",
)
