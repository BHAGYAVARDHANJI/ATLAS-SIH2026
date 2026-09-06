import streamlit as st
from data import inject_custom_css, sidebar_profile_switcher, require_profile, require_login, generate_quiz, save_progress

st.set_page_config(page_title="ATLAS | AI Quiz", page_icon="📝", layout="wide")
inject_custom_css()
require_login()
sidebar_profile_switcher()
profile = require_profile()

st.title("📝 AI-Generated Quiz")
st.divider()

if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_source" not in st.session_state:
    st.session_state.quiz_source = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

top1, top2 = st.columns([3, 1])
with top1:
    n_questions = st.slider("Number of questions", 5, 15, 10)
with top2:
    st.write("")
    if st.button("🔄 Generate New Quiz", use_container_width=True):
        with st.spinner("Generating your quiz..."):
            questions, source = generate_quiz(n_questions, profile_id=st.session_state.selected_profile)
        st.session_state.current_quiz = questions
        st.session_state.quiz_source = source
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False

quiz = st.session_state.current_quiz

if not quiz:
    st.info("Click **Generate New Quiz** to begin.")
    st.stop()

if st.session_state.quiz_source == "ai":
    st.caption("🤖 AI-generated quiz, personalized to your biggest skill gaps.")
else:
    st.caption("📦 Showing the built-in fallback quiz (AI unavailable right now).")

answered = len(st.session_state.quiz_answers)
st.progress(answered / len(quiz), text=f"{answered}/{len(quiz)} answered")

for i, q in enumerate(quiz):
    with st.container(border=True):
        st.markdown(f"**Q{i+1}. {q['q']}**")
        choice = st.radio(
            "Choose one:", options=list(range(len(q["options"]))),
            format_func=lambda idx, opts=q["options"]: opts[idx],
            key=f"quiz_q_{i}", index=None, label_visibility="collapsed",
        )
        st.session_state.quiz_answers[i] = choice

        if st.session_state.quiz_submitted:
            if choice == q["answer"]:
                st.success("✅ Correct")
            else:
                st.error(f"❌ Correct answer: {q['options'][q['answer']]}")

st.divider()
c1, c2 = st.columns([1, 3])
with c1:
    if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
        st.session_state.quiz_submitted = True
        score = sum(1 for i, q in enumerate(quiz) if st.session_state.quiz_answers.get(i) == q["answer"])
        total = len(quiz)
        save_progress(st.session_state.selected_profile, score, total)
        st.rerun()

if st.session_state.quiz_submitted:
    score = sum(1 for i, q in enumerate(quiz) if st.session_state.quiz_answers.get(i) == q["answer"])
    total = len(quiz)
    st.metric("Your Score", f"{score}/{total}", f"{round(score/total*100)}%")
    st.page_link("pages/5_Progress.py", label="Next: View Progress →", icon="📈")