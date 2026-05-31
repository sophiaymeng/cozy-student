import streamlit as st

from agents.student_agent import StudentAgent, build_student_prompt
from agents.learning_outcomes_agent import LearningOutcomesAgent
from agents.llm_actor3_verifier import LLMActor3Verifier


st.set_page_config(page_title="Cozy Student", layout="centered")


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

    /* Apply Quicksand only to known text containers — leave Streamlit's chrome (icons, etc.) alone */
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stChatMessageContent"],
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatInput"] textarea,
    [data-testid="stCaptionContainer"],
    .stButton > button {
        font-family: 'Quicksand', system-ui, sans-serif !important;
    }

    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    [data-testid="stChatInput"] > div {
        border-radius: 28px !important;
        border: 1px solid #D9CFBE !important;
        background-color: #FFFEFA !important;
    }

    [data-testid="stChatInput"] div,
    [data-testid="stChatInput"] textarea {
        background-color: #FFFEFA !important;
    }

    [data-testid="stChatInput"] textarea {
        font-size: 15px !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stButton button {
        border-radius: 20px !important;
        border: 1px solid #D9CFBE !important;
        background-color: #FFFEFA !important;
        color: #3D3528 !important;
    }

    .stButton button:hover {
        background-color: #F5EEDC !important;
        border-color: #8B9A7D !important;
    }

    [data-testid="stChatMessage"] {
        padding: 12px 4px !important;
    }

    [data-testid="stSidebar"] {
        background-color: #F5EEDC !important;
    }

    .block-container {
        padding-top: 3rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


GREETING_WORDS = {
    "hi", "hello", "hey", "yo", "sup", "hola", "howdy", "hai",
    "good morning", "good afternoon", "good evening", "what's up", "whats up",
    "how are you", "how's it going", "hows it going",
}


def looks_like_greeting(text: str) -> bool:
    """Heuristic: short casual messages that aren't a topic to teach."""
    t = text.strip().lower().rstrip("!.?")
    if len(t) < 4:
        return True
    if t in GREETING_WORDS:
        return True
    first = t.split()[0] if t.split() else ""
    if first in {"hi", "hello", "hey", "yo", "sup", "hola"} and len(t) < 20:
        return True
    return False


def init_session():
    st.session_state.agent = StudentAgent()
    st.session_state.outcomes_agent = LearningOutcomesAgent()
    st.session_state.verifier = LLMActor3Verifier()
    st.session_state.messages = []
    st.session_state.topic = None
    st.session_state.all_user_text = []
    st.session_state.verifier_warnings = {}


if "agent" not in st.session_state:
    init_session()


with st.sidebar:
    st.markdown("### Cozy")
    st.caption("a little learner who asks back")
    st.divider()

    oa = st.session_state.outcomes_agent
    if st.session_state.topic:
        st.markdown("**Topic**")
        st.markdown(st.session_state.topic)
        st.divider()

    if oa.outcomes:
        st.markdown("**Learning objectives**")
        covered = oa.coverage.get("covered", [])
        partial = oa.coverage.get("partial", [])
        for outcome in oa.outcomes:
            if outcome in covered:
                icon = "✓"
            elif outcome in partial:
                icon = "~"
            else:
                icon = "○"
            st.markdown(f"{icon}  {outcome}")
        st.divider()
        score = oa.mastery_score()
        st.progress(score / 100, text=f"Mastery: {score}%")
        st.divider()

    if st.button("Start fresh", use_container_width=True):
        init_session()
        st.rerun()


if not st.session_state.messages:
    st.markdown("## Hey, what are we learning today?")
    st.caption("Tell me a topic to start, then teach me until I really get it.")


for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
    if msg["role"] == "assistant":
        warnings = st.session_state.verifier_warnings.get(i)
        if warnings:
            st.warning("Verifier flagged: " + "; ".join(warnings))


if prompt := st.chat_input("Teach Cozy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.topic is None:
        if looks_like_greeting(prompt):
            greeting_prompt = (
                f"The user just greeted you with: '{prompt}'. "
                "Greet them back warmly as a curious student in one short sentence, "
                "then ask what topic they'd like to teach you today."
            )
            with st.chat_message("assistant"):
                reply = st.write_stream(st.session_state.agent.respond_stream(greeting_prompt))
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.session_state.topic = prompt
            with st.spinner("Generating learning outcomes...", expanded=False):
                st.session_state.outcomes_agent.generate_outcomes(prompt)

            with st.chat_message("assistant"):
                opener = st.write_stream(
                    st.session_state.agent.respond_stream(
                        f"I want to learn about: {prompt}. Could you start by telling me what it is?"
                    )
                )
            st.session_state.messages.append({"role": "assistant", "content": opener})
    else:
        st.session_state.all_user_text.append(prompt)

        with st.spinner("Checking coverage...", expanded=False):
            coverage = st.session_state.outcomes_agent.evaluate_coverage(
                " ".join(st.session_state.all_user_text)
            )
            gap = st.session_state.outcomes_agent.next_gap()

        steered = build_student_prompt(prompt, gap, coverage)
        with st.chat_message("assistant"):
            reply = st.write_stream(st.session_state.agent.respond_stream(steered))
        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.spinner("Verifying truthfulness...", expanded=False):
            result = st.session_state.verifier.verify_conversation(
                st.session_state.agent.history
            )
        if not result.get("is_truthful") and result.get("wrong"):
            idx = len(st.session_state.messages) - 1
            st.session_state.verifier_warnings[idx] = result["wrong"]

    st.rerun()
