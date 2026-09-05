import streamlit as st
import pandas as pd
import plotly.express as px
from data import inject_custom_css, sidebar_profile_switcher, require_profile

st.set_page_config(page_title="ATLAS | Progress", page_icon="📈", layout="wide")
inject_custom_css()
sidebar_profile_switcher()
profile = require_profile()

st.title("📈 Progress Dashboard")
st.divider()

log = st.session_state.get("progress_log", [])

if not log:
    st.info("No quiz attempts yet. Complete a quiz to see progress here.")
    st.page_link("pages/4_AI_Quiz.py", label="Take a Quiz →", icon="📝")
    st.stop()

df = pd.DataFrame(log)
df["percent"] = (df["score"] / df["total"] * 100).round(1)
df["attempt"] = range(1, len(df) + 1)

c1, c2, c3 = st.columns(3)
c1.metric("Attempts", len(df))
c2.metric("Latest Score", f"{df.iloc[-1]['score']}/{df.iloc[-1]['total']}", f"{df.iloc[-1]['percent']}%")
c3.metric("Best Score", f"{df['percent'].max()}%")

st.subheader("Score Trend")
fig = px.line(df, x="attempt", y="percent", markers=True,
              labels={"attempt": "Attempt #", "percent": "Score (%)"})
fig.update_traces(line_color="#4F8BF9", marker=dict(size=9))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#FAFAFA", height=380, yaxis_range=[0, 100],
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Attempt Log")
st.dataframe(df[["attempt", "score", "total", "percent"]], use_container_width=True, hide_index=True)
