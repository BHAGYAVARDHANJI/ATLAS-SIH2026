import streamlit as st

from data import (
    inject_custom_css,
    sidebar_profile_switcher,
    require_profile,
    require_login,
    generate_quiz,
    save_progress,
)

st.set_page_config(
    page_title="ATLAS | AI Quiz",
    page_icon="📝",
    layout="wide",
)

inject_custom_css()
require_login()
sidebar_profile_switcher()
profile = require_profile()

st.title("📝 AI-Generated Quiz")
st.divider()

# ---------------------------------------------------------
# QUIZ STATE
# ---------------------------------------------------------
defaults = {
    "current_quiz": None,
    "quiz_source": None,
    "quiz_answers": {},
    "quiz_submitted": False,
    "quiz_score": None,
    "quiz_version": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# GENERATE NEW QUIZ
# ---------------------------------------------------------
top1, top2 = st.columns([3, 1])

with top1:
    n_questions = st.slider(
        "Number of questions",
        min_value=5,
        max_value=15,
        value=10,
    )

with top2:
    st.write("")
    if st.button("🔄 Generate New Quiz", width="stretch"):
        with st.spinner("Generating your quiz..."):
            questions, source = generate_quiz(
                n_questions,
                profile_id=profile["id"],
            )

        # Change the widget key namespace so old radio-button answers
        # cannot leak into the newly generated quiz.
        st.session_state.quiz_version += 1
        st.session_state.current_quiz = questions
        st.session_state.quiz_source = source
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False
        st.session_state.quiz_score = None
        st.rerun()

quiz = st.session_state.current_quiz

if not quiz:
    st.info("Click **Generate New Quiz** to begin.")
    st.stop()

# ---------------------------------------------------------
# QUIZ SOURCE + PROGRESS
# ---------------------------------------------------------
if st.session_state.quiz_source == "ai":
    st.caption("🤖 AI-generated quiz, personalized to your biggest skill gaps.")
else:
    st.caption("📦 Built-in fallback quiz is being used because AI generation is unavailable.")

answered = sum(
    answer is not None
    for answer in st.session_state.quiz_answers.values()
)

st.progress(
    answered / len(quiz),
    text=f"{answered}/{len(quiz)} answered",
)

# ---------------------------------------------------------
# QUESTIONS
# ---------------------------------------------------------
version = st.session_state.quiz_version

for i, q in enumerate(quiz):
    with st.container(border=True):
        st.markdown(f"**Q{i + 1}. {q['q']}**")

        widget_key = f"quiz_q_{version}_{i}"

        choice = st.radio(
            "Choose one:",
            options=list(range(len(q["options"]))),
            format_func=lambda idx, opts=q["options"]: opts[idx],
            key=widget_key,
            index=None,
            label_visibility="collapsed",
            disabled=st.session_state.quiz_submitted,
        )

        # Only store a real selection. Do not turn an untouched question
        # into an attempted answer.
        if choice is not None:
            st.session_state.quiz_answers[i] = choice

        # Results are shown only after a successful submission.
        if st.session_state.quiz_submitted:
            selected = st.session_state.quiz_answers.get(i)

            if selected == q["answer"]:
                st.success("✅ Correct")
            else:
                st.error(
                    f"❌ Correct answer: {q['options'][q['answer']]}"
                )

# ---------------------------------------------------------
# SUBMIT
# ---------------------------------------------------------
st.divider()

if not st.session_state.quiz_submitted:
    if st.button(
        "✅ Submit Quiz",
        type="primary",
        width="stretch",
    ):
        unanswered = [
            i + 1
            for i in range(len(quiz))
            if st.session_state.quiz_answers.get(i) is None
        ]

        if unanswered:
            st.warning(
                "⚠️ Please answer all questions before submitting. "
                f"Unanswered question(s): {', '.join(map(str, unanswered))}"
            )
        else:
            score = sum(
                1
                for i, q in enumerate(quiz)
                if st.session_state.quiz_answers.get(i) == q["answer"]
            )

            total = len(quiz)

            # Persist exactly once for this quiz submission.
            save_progress(
                profile["id"],
                score,
                total,
            )

            st.session_state.quiz_score = score
            st.session_state.quiz_submitted = True
            st.rerun()

# ---------------------------------------------------------
# RESULT
# ---------------------------------------------------------
if st.session_state.quiz_submitted:
    score = st.session_state.quiz_score
    total = len(quiz)
    percentage = round(score / total * 100, 1)

    st.divider()
    st.success(
        f"🎉 Quiz submitted successfully — Score: "
        f"**{score}/{total} ({percentage}%)**"
    )

    if st.button("📈 Next: View Progress →", type="primary", width="stretch"):
        st.switch_page("pages/5_Progress.py")
