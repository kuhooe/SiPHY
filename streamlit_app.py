# ✅ streamlit_app.py — SiPHY Protocol Assistant UI (FIXED and CLEAN)

import streamlit as st
from constants import MODES
from clause_feedback import save_query_history
from ethernet_bot import answer_ethernet_query
from utils import parse_sectioned_response

# Initialize session state
if "questions" not in st.session_state:
    st.session_state["questions"] = []
if "answers" not in st.session_state:
    st.session_state["answers"] = []

# Sidebar
st.sidebar.markdown("### Query Mode")
st.session_state["mode"] = st.sidebar.selectbox(
    "Choose reasoning mode:",
    options=MODES,
    index=MODES.index(st.session_state.get("mode", "Smart Designer"))
)

if st.sidebar.button("Export Chat as PDF"):
    st.warning("PDF export not wired up in this version.")

with st.sidebar.expander("ℹ️ About SiPHY"):
    st.markdown("**Protocol design assistant using OpenAI + FAISS + clause metadata.**")

# Header
st.image("siemens_logo.png", width=100)
st.title("SiPHY Protocol Assistant")

# Show chat history
for q, a in zip(st.session_state["questions"], st.session_state["answers"]):
    with st.chat_message("user"): st.markdown(q)
    with st.chat_message("assistant"): st.markdown(a)

# Input
user_query = st.chat_input("Ask a protocol question (Ethernet, PCIe, UCIE...)")
if user_query:
    with st.chat_message("user"): st.markdown(user_query)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing protocol clauses..."):
            try:
                answer, clauses = answer_ethernet_query(user_query, st.session_state["mode"])
                parsed = parse_sectioned_response(answer)
                if parsed.strip():
                    answer = parsed
            except Exception as e:
                answer = f"Error generating answer: {e}"
                clauses = []

        st.markdown(answer)
        st.session_state["questions"].append(user_query)
        st.session_state["answers"].append(answer)
        save_query_history(user_query, answer, clauses)
