import streamlit as st
import re

from data import render_html


def normalize(text: str) -> str:
    """Normalize user input for simple intent matching."""
    return re.sub(r"\s+", " ", text.strip().lower())


def get_skill_context(gap_rows):
    """Create useful context from the current learner's skill-gap data."""
    if not gap_rows:
        return None

    sorted_rows = sorted(
        gap_rows,
        key=lambda x: float(x.get("gap", 0)),
        reverse=True,
    )

    top = sorted_rows[0]

    high = [
        row["competency"]
        for row in sorted_rows
        if row.get("priority") == "High"
    ]

    medium = [
        row["competency"]
        for row in sorted_rows
        if row.get("priority") == "Medium"
    ]

    return {
        "top": top,
        "high": high,
        "medium": medium,
        "all": sorted_rows,
    }


def generate_response(message, profile=None, gap_rows=None):
    """
    Free ATLAS assistant.

    It does not call any paid API.
    Responses are generated using the learner's actual
    profile and competency data.
    """

    text = normalize(message)
    context = get_skill_context(gap_rows)

    name = profile.get("name", "Learner") if profile else "Learner"
    role = profile.get("role", "your role") if profile else "your role"

    if not text:
        return (
            "Hi! 👋 I'm **ATLAS Assistant**.\n\n"
            "I can help you understand your skill gaps, "
            "priorities, recommendations, quiz preparation, "
            "and learning progress."
        )

    # ---------------------------------------------------------
    # GREETING
    # ---------------------------------------------------------
    greetings = [
        "hi",
        "hello",
        "hey",
        "hii",
        "good morning",
        "good afternoon",
        "good evening",
    ]

    if text in greetings or any(text.startswith(g + " ") for g in greetings):
        return (
            f"Hello **{name}**! 👋\n\n"
            f"I'm your **ATLAS Assistant** for the role of "
            f"**{role}**.\n\n"
            "You can ask me things like:\n"
            "- What is my biggest skill gap?\n"
            "- What should I improve first?\n"
            "- Why is this skill a priority?\n"
            "- Give me a learning plan.\n"
            "- How can I improve my weakest skill?\n"
            "- Help me prepare for the quiz."
        )

    if context is None:
        return (
            "I don't have the learner's competency data available yet. "
            "Please open the **Competency Skill Gap** page first."
        )

    top = context["top"]
    competency = top["competency"]
    current = top["current"]
    required = top["required"]
    gap = top["gap"]
    priority = top["priority"]

    # ---------------------------------------------------------
    # BIGGEST / WEAKEST SKILL
    # ---------------------------------------------------------
    if (
        ("biggest" in text and "gap" in text)
        or "largest gap" in text
        or "weakest skill" in text
        or "weakest competency" in text
        or "most important skill" in text
    ):
        return (
            f"### 🎯 Your biggest skill gap\n\n"
            f"**{competency}** is currently your biggest development "
            f"priority.\n\n"
            f"- Current level: **{current}**\n"
            f"- Required level: **{required}**\n"
            f"- Gap: **{gap}**\n"
            f"- Priority: **{priority}**\n\n"
            f"### What this means\n"
            f"Your current competency in **{competency}** is below "
            f"the level expected for your role. This makes it the "
            f"best place to start your development journey."
        )

    # ---------------------------------------------------------
    # WHAT SHOULD I IMPROVE
    # ---------------------------------------------------------
    if (
        "what should i improve" in text
        or "what should i learn" in text
        or "where should i start" in text
        or "improve first" in text
        or "learn first" in text
        or "next skill" in text
    ):
        answer = (
            f"### 🚀 Recommended starting point\n\n"
            f"Start with **{competency}**.\n\n"
            f"Your current level is **{current}**, while the required "
            f"level is **{required}**, giving you a gap of **{gap}**.\n\n"
            f"Because this is your largest identified gap, improving "
            f"this competency should give you the strongest immediate "
            f"development impact."
        )

        if context["high"]:
            answer += (
                "\n\n### 🔴 Other high-priority skills\n"
                + "\n".join(f"- {skill}" for skill in context["high"])
            )

        if context["medium"]:
            answer += (
                "\n\n### 🟡 Medium-priority skills\n"
                + "\n".join(f"- {skill}" for skill in context["medium"])
            )

        return answer

    # ---------------------------------------------------------
    # WHY PRIORITY
    # ---------------------------------------------------------
    if (
        "why" in text
        and (
            "priority" in text
            or "important" in text
            or "gap" in text
        )
    ):
        return (
            f"### 💡 Why {competency} is a priority\n\n"
            f"The assessment shows:\n\n"
            f"**Current:** {current}\n\n"
            f"**Required:** {required}\n\n"
            f"**Gap:** {gap}\n\n"
            f"Since this is the largest identified gap, ATLAS places "
            f"**{competency}** at the top of the development plan."
        )

    # ---------------------------------------------------------
    # LEARNING PLAN
    # ---------------------------------------------------------
    if (
        "learning plan" in text
        or "study plan" in text
        or "roadmap" in text
        or "how can i improve" in text
        or "how to improve" in text
    ):
        return (
            f"### 📚 Your ATLAS learning plan\n\n"
            f"**Primary focus:** {competency}\n\n"
            f"**Current level:** {current}\n\n"
            f"**Target level:** {required}\n\n"
            f"**Gap:** {gap}\n\n"
            f"#### Suggested approach\n"
            f"1. Review the fundamentals of **{competency}**.\n"
            f"2. Practice small problems or real-world exercises.\n"
            f"3. Apply the skill to a practical task related to your role.\n"
            f"4. Take the ATLAS quiz to test your understanding.\n"
            f"5. Reassess your competency and track the improvement.\n\n"
            f"Your goal should be to gradually reduce the gap rather "
            f"than trying to improve everything at once."
        )

    # ---------------------------------------------------------
    # QUIZ
    # ---------------------------------------------------------
    if (
        "quiz" in text
        or "test me" in text
        or "question" in text
        or "prepare me" in text
    ):
        return (
            f"### 🧠 Quiz preparation\n\n"
            f"I recommend focusing your preparation on "
            f"**{competency}** because it currently has the largest "
            f"identified gap.\n\n"
            f"Open **AI Quiz** from the sidebar to test your knowledge.\n\n"
            f"Before starting, revise:\n"
            f"- Core concepts\n"
            f"- Practical applications\n"
            f"- Common mistakes\n"
            f"- Role-specific use cases"
        )

    # ---------------------------------------------------------
    # ALL SKILLS
    # ---------------------------------------------------------
    if (
        "all skills" in text
        or "show skills" in text
        or "skill gaps" in text
        or "my gaps" in text
        or "competencies" in text
    ):
        lines = ["### 📊 Your competency overview\n"]

        for row in context["all"]:
            lines.append(
                f"- **{row['competency']}** — "
                f"Current: {row['current']} · "
                f"Required: {row['required']} · "
                f"Gap: {row['gap']} · "
                f"Priority: {row['priority']}"
            )

        return "\n".join(lines)

    # ---------------------------------------------------------
    # PROFILE
    # ---------------------------------------------------------
    if (
        "who am i" in text
        or "my profile" in text
        or "my role" in text
        or "about me" in text
    ):
        qualification = (
            profile.get("qualification")
            or profile.get("qualifications")
            or "Not specified"
        )

        return (
            f"### 👤 Your ATLAS profile\n\n"
            f"**Name:** {name}\n\n"
            f"**Role:** {role}\n\n"
            f"**Qualification:** {qualification}\n\n"
            f"Your competency assessment is being used to identify "
            f"the skills that will have the highest development priority."
        )

    # ---------------------------------------------------------
    # RECOMMENDATIONS
    # ---------------------------------------------------------
    if (
        "recommend" in text
        or "recommendation" in text
        or "suggest" in text
    ):
        return (
            f"### 🎯 ATLAS recommendation\n\n"
            f"Your first recommendation is to work on "
            f"**{competency}**.\n\n"
            f"After addressing this gap, move to the next "
            f"high-priority competency and then the medium-priority "
            f"ones.\n\n"
            f"You can open **Recommendations** from the sidebar "
            f"for the detailed development suggestions."
        )

    # ---------------------------------------------------------
    # THANKS
    # ---------------------------------------------------------
    if any(word in text for word in ["thank you", "thanks", "thank"]):
        return (
            "You're welcome! 😊\n\n"
            "I'm here whenever you want to understand your "
            "skill gaps or plan your next learning step."
        )

    # ---------------------------------------------------------
    # DEFAULT INTELLIGENT FALLBACK
    # ---------------------------------------------------------
    return (
        f"I can help you with your ATLAS assessment, **{name}**.\n\n"
        f"Based on your current assessment, your strongest development "
        f"focus is **{competency}** with a gap of **{gap}**.\n\n"
        "Try asking me:\n"
        "- **What is my biggest skill gap?**\n"
        "- **What should I improve first?**\n"
        "- **Why is this skill a priority?**\n"
        "- **Give me a learning plan.**\n"
        "- **Show me all my skill gaps.**\n"
        "- **Help me prepare for the quiz.**"
    )


def render_chatbot(profile=None, gap_rows=None):
    """Render the ATLAS chatbot UI."""

    st.markdown(
        """
        <style>
        .atlas-chat-header {
            padding: 18px 20px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(108,108,255,.20), rgba(55,214,196,.14));
            border: 1px solid rgba(255,255,255,.08);
            margin-bottom: 18px;
        }
        .atlas-chat-title {
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 4px;
            font-family: 'Sora', sans-serif;
        }
        .atlas-chat-subtitle {
            color: #9BA0B4;
            font-size: .92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    render_html("""
    <div class="atlas-chat-header">
        <div class="atlas-chat-title">🤖 ATLAS Assistant</div>
        <div class="atlas-chat-subtitle">Your personal skill-gap and learning assistant</div>
    </div>
    """)

    if "atlas_chat_messages" not in st.session_state:
        st.session_state.atlas_chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! 👋 I'm **ATLAS Assistant**.\n\n"
                    "I can help you understand your skill gaps, "
                    "priorities and learning plan."
                ),
            }
        ]

    for message in st.session_state.atlas_chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input(
        "Ask ATLAS about your skills, gaps or learning plan..."
    )

    if user_message:
        st.session_state.atlas_chat_messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        response = generate_response(
            user_message,
            profile=profile,
            gap_rows=gap_rows,
        )

        st.session_state.atlas_chat_messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        st.rerun()


def clear_chat():
    """Clear ATLAS chat history."""
    st.session_state.pop("atlas_chat_messages", None)