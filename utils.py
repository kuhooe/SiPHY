# 📦 Dependency Setup
import os
import json
from dotenv import load_dotenv
import tiktoken
import streamlit as st
from datetime import datetime
from fpdf import FPDF
import faiss
import numpy as np
from openai import OpenAI

import streamlit as st
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
print("✅ Loaded OpenAI Key:", st.secrets["OPENAI_API_KEY"][:10])


# 💬 OpenAI Answer Generator
def get_openai_answer(query, context, mode, sources=None):
    if mode == "Expert Context Mode":
        system_prompt = (
            "You are a helpful Ethernet specification assistant. Provide technically accurate answers using IEEE clause data, metadata summaries, and real-world vendor sources."
            " Cite all used clauses at the end under a 'Citations' section. Responses should be factual, dense with technical detail, and free from unnecessary conversational language."
        )
    elif mode == "Smart Designer":
        system_prompt = (
            "You are a helpful Ethernet specification assistant. Use all clause data from metadata.json including IEEE specifications and external vendor sources such as whitepapers. "
            "Begin with a short summary paragraph that directly answers the user's question in 2–4 sentences. "
            "Then format your response in 3 clear sections with these exact headings: 'Tradeoffs:', 'Caveats:', and 'Real-World Context:' "
            "Do not repeat section titles in the body. Use clause data and industry context to support each one. Avoid emojis or conversational language."
        )
    else:
        system_prompt = (
            "You are a rules-based Ethernet specification assistant. You may only return exact IEEE clause summaries without any opinions, caveats, tradeoffs, or external context."
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {query}\n\nContext:\n{context}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",  # ✅ This is GPT-4.1
        messages=messages,
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()

    if mode == "Smart Designer":
        content = f"[Smart Designer Mode]\n\n{content}"
    elif mode == "Expert Context Mode":
        content = f"[Expert Context Mode]\n\n{content}"

    if mode == "Expert Context Mode" and sources:
        clause_list = sorted(set(s.get("clause") or s.get("ref") for s in sources if s.get("clause") or s.get("ref")))
        if clause_list:
            content += "\n\n**Citations**\n"
            content += "\n".join(f"- {c}" for c in clause_list)

    return content


# 🧠 Embedding Generator
def get_embedding(text, model="text-embedding-3-small"):
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0]["embedding"]

# 🫠 Session State Initialization
def init_session_state():
    for key in ["questions", "answers", "last_clauses", "history"]:
        if key not in st.session_state:
            st.session_state[key] = []

# 📂 Chat History Saver
def save_query_history(question, answer, clauses):
    entry = {
        "question": question,
        "answer": answer,
        "clauses": clauses
    }
    st.session_state["history"].append(entry)

# 📜 PDF Exporter
def generate_pdf(history):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for item in history:
        pdf.multi_cell(0, 10, f"Q: {item['question']}", align="L")
        pdf.multi_cell(0, 10, f"A: {item['answer']}", align="L")
        if item.get("clauses"):
            for clause in item["clauses"]:
                pdf.multi_cell(0, 10, f"- Clause {clause['clause_number']}: {clause['title']}", align="L")
        pdf.ln(5)

    return pdf.output(dest="S").encode("latin1")

def export_chat_history_to_pdf(questions, answers):
    os.makedirs("exports", exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_title("SiPHY Assistant Chat")
    pdf.cell(200, 10, txt="SiPHY Assistant Chat History", ln=True, align="C")

    for i, (q, a) in enumerate(zip(questions, answers)):
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(0, 10, f"Q{i+1}: {q}")
        pdf.set_font("Arial", style="", size=12)
        pdf.multi_cell(0, 10, f"A{i+1}: {a}")
        pdf.ln(5)

    filename = f"exports/chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)

# 🧠 Clause Formatter for Prompt Context
def format_clause_context(clauses, mode):
    context = ""
    for clause in clauses:
        context += f"Clause {clause['clause_number']}: {clause['title']}\n"
        context += f"Summary: {clause['summary']}\n"

        if mode == "Smart Designer":
            if "tradeoffs" in clause:
                context += f"Tradeoffs: {clause['tradeoffs']}\n"
            if "caveats" in clause:
                context += f"Caveats: {clause['caveats']}\n"
            if "external_context" in clause:
                context += f"Real-World Context: {clause['external_context']}\n"

        elif mode == "Expert Context Mode":
            context += f"Context: {clause.get('external_context', '')}\n"

        context += "\n"
    return context

# 🥥 Finalized Section Parser with Mode Tag, Summary, and Proper Sections
def parse_sectioned_response(response_text):
    mode_header = "**[Smart Designer Mode]**\n\n"

    # Remove mode label (non-bold) from start
    cleaned = response_text.strip()
    if cleaned.startswith("[Smart Designer Mode]"):
        cleaned = cleaned[len("[Smart Designer Mode]"):].strip()

    section_headers = ["Tradeoffs", "Caveats", "Real-World Context"]
    sections = {header: "" for header in section_headers}

    summary_lines = []
    current_section = None

    for line in cleaned.splitlines():
        stripped = line.strip()
        matched = next((h for h in section_headers if stripped.lower().startswith(h.lower())), None)
        if matched:
            current_section = matched
        elif current_section:
            sections[current_section] += line + "\n"
        else:
            summary_lines.append(line)

    # Rebuild formatted output
    formatted = mode_header
    if summary_lines:
        formatted += "\n".join(summary_lines).strip() + "\n\n"

    for header in section_headers:
        formatted += f"**{header}**\n\n{sections[header].strip()}\n\n"

    return formatted.strip()

# 🗕️ FAISS-Based Semantic Clause Retrieval
VECTORSTORE_PATH = "vectorstore/faiss.index"
EMBEDDINGS_PATH = "vectorstore/clause_embeddings.npy"
METADATA_PATH = "metadata.json"

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    METADATA = json.load(f)

FAISS_INDEX = faiss.read_index(VECTORSTORE_PATH)
CLAUSE_EMBEDDINGS = np.load(EMBEDDINGS_PATH)

def retrieve_relevant_clauses(prompt, mode, top_k=3):
    embed_response = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
    query_embedding = np.array(embed_response.data[0].embedding, dtype="float32").reshape(1, -1)
    distances, indices = FAISS_INDEX.search(query_embedding, top_k)
    results = []
    for idx in indices[0]:
        if 0 <= idx < len(METADATA):
            results.append(METADATA[idx])
    return results
