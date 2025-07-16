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
    generate_pdf,
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
            history = list(zip(st.session_state["questions"], st.session_state["answers"]))
            filename = generate_pdf("questions", "answers")
            st.success("Chat history exported successfully.")
            st.markdown(f"[📄 Download PDF]({filename})", unsafe_allow_html=True)
        else:
            st.warning("No chat history to export.")

    with st.expander("ℹ️ About SiPHY"):
    st.markdown("""
**SiPHY** is a multi-mode protocol assistant trained on multiple IP Protocols (Ethernet, UCIE, PCIe...) specifications. It is powered by FAISS + OpenAI + custom clause metadata.  

**Use it today to:** 
- Clarify protocol behavior  
- Compare design tradeoffs (e.g., PAM4 vs NRZ)  
- Compare encoding schemes (e.g., 64b/66b vs 8b/10b)  

**In the Future**  
- Simulate edge cases or debug scenarios  
- Debug protocol interoperability  
- Validate clause coverage in chiplet designs  
- Explore derivative design options  

### Potential Use Cases

**1. Protocol Coach Mode**  
• Teaches engineers the functional behavior of protocols  
• Answers live questions like:  
  o “What happens in the PCIe Gen5 equalization phase?”  
  o “What’s the role of training sequences in 100G Ethernet?”  
  o “Explain LTSSM state transitions with timing constraints.”

**2. Use-Case Driven Guidance**  
• Offers protocol advice in the context of system goals:  
  o “Which Ethernet mode (10GBASE-KR vs 10GBASE-R) is better for low-power backplane?”  
  o “Can I use PCIe Gen4 over retimers for a latency-sensitive accelerator?”

**3. IP Config Advisor**  
• Helps designers configure IPs with protocol options to meet PPA goals  
• Examples:  
  o “Which lane bonding options are valid for PCIe Gen5 x16 in this floorplan?”  
  o “Can I disable replay buffer if I don’t need retry in SRIOV mode?”

**4. Protocol Debug Assistant**  
• Helps analyze protocol-level bugs from simulation/emulation/test logs  
• Examples:  
  o “Why does my PCIe link get stuck in Recovery.RcvrCfg?”  
  o “Why are FEC errors spiking under 100G Ethernet load?”
""")

# 📄 Sample Questions Viewer
    if os.path.exists("sample_questions.txt"):
        with open("sample_questions.txt", "r") as f:
            sample_qs_text = f.read()
        with st.expander("📄 View All Sample Questions"):
            st.text_area("Sample Questions", value=sample_qs_text, height=300, disabled=False)
        
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
    "Why shouldn't you use 8b/10b encoding in 10G Ethernet?",
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
