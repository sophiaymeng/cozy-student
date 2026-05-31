import streamlit as st
from agents.student_agent import StudentAgent


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

    [data-testid="stChatInput"] textarea {
        font-size: 15px !important;
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


if "agent" not in st.session_state:
    st.session_state.agent = StudentAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.markdown("### Cozy")
    st.caption("a little learner who asks back")
    st.divider()
    if st.button("Start fresh", use_container_width=True):
        st.session_state.agent = StudentAgent()
        st.session_state.messages = []
        st.rerun()


if not st.session_state.messages:
    st.markdown("## Hey, what are we learning today?")
    st.caption("Teach me something. I'll keep asking until I really get it.")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("Start explaining..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_reply = st.write_stream(st.session_state.agent.respond_stream(prompt))

    st.session_state.messages.append({"role": "assistant", "content": full_reply})
