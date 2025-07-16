# ✅ streamlit_app.py — SiPHY Protocol Assistant UI (Restored & Working)

import streamlit as st
import os
from datetime import datetime
import streamlit.components.v1 as components

from constants import MODES, APP_NAME
from utils import (
    init_session_state,
    format_clause_context,
    parse_sectioned_response,
    export_chat_history_to_pdf,
    save_query_history,
)
from ethernet_bot import answer_ethernet_query

# Init
os.makedirs("exports", exist_ok=True)
init_session_state()

# 💄 Styling
components.html("""
<style>
html, body, [class*='css'] {
    zoom: 100%;
    font-family: 'Segoe UI', sans-serif;
    background-color: white;
    color: black;
    line-height: 1.6;
}
section[data-testid="stSidebar"] + section main div:first-child {
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
div[data-testid="stChatMessage"] {
    margin: 0.5rem 0;
    padding: 0.75rem;
    background-color: #f8f9fa;
    border-radius: 6px;
}
</style>
""", height=0)

# Sidebar
with st.sidebar:
    st.markdown("### Query Mode")
    st.session_state["mode"] = st.selectbox(
        "Choose reasoning mode:",
        options=MODES,
        index=MODES.index(st.session_state.get("mode", "Smart Designer"))
    )

   if st.button("Export Chat as PDF"):
    if st.session_state["questions"]:
        filename = export_chat_history_to_pdf(
            st.session_state["questions"], st.session_state["answers"]
        )
        st.success("Chat history exported successfully.")
        st.markdown(f"[📄 Download PDF]({filename})", unsafe_allow_html=True)
    else:
        st.warning("No chat history to export.")

    with st.expander("ℹ️ About SiPHY"):
        st.markdown("**Protocol design assistant using OpenAI + FAISS + clause metadata.**")

    if os.path.exists("sample_questions.txt"):
        with open("sample_questions.txt", "r") as f:
            st.text_area("Sample Questions", f.read(), height=300, disabled=True)

# Header
st.image("siemens_logo.png", width=100)
st.title(APP_NAME)

if "hide_warning" not in st.session_state:
    st.session_state["hide_warning"] = False

if not st.session_state["hide_warning"]:
    st.warning("⚠️ If you see `Failed to fetch dynamically imported module` error, clear browser cache (Ctrl+Shift+R).")
    if st.button("Dismiss warning"):
        st.session_state["hide_warning"] = True

# History
for q, a in zip(st.session_state["questions"], st.session_state["answers"]):
    with st.chat_message("user"): st.markdown(q)
    with st.chat_message("assistant"): st.markdown(a)

# Suggestions
sample_questions = [
    "What is 64b/66b encoding and why is it used in Ethernet?",
    "How does Clause 91 RS-FEC help reduce packet drops?",
    "What happens during lane deskew in 25GBASE-R?",
    "Why not use 8b/10b encoding in 10G Ethernet?",
    "Can you do \"bump on a wire\" design that does not require a Zynq device?"
]
st.markdown("**Try asking:**")
cols = st.columns(len(sample_questions))
for i, q in enumerate(sample_questions):
    if cols[i].button(q):
        st.session_state["pending_query"] = q

# Input
user_query = st.chat_input("Ask a protocol question (Ethernet, PCIe, UCIE...)")
if user_query:
    st.session_state["pending_query"] = user_query

# Query Processing
if "pending_query" in st.session_state:
    q = st.session_state.pop("pending_query")
    with st.chat_message("user"): st.markdown(q)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing protocol clauses..."):
            try:
                answer, clauses = answer_ethernet_query(q, st.session_state["mode"])
                parsed = parse_sectioned_response(answer)
                if parsed.strip():
                    answer = parsed
            except Exception as e:
                answer = f"Error generating answer: {e}"
                clauses = []

        st.markdown(answer)
        st.session_state["questions"].append(q)
        st.session_state["answers"].append(answer)
        save_query_history(q, answer, clauses)
