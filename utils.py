# ✅ utils.py — Core Logic for SiPHY Assistant

import openai
import json
import os
from constants import METADATA_FILE
from fpdf import FPDF
from datetime import datetime

client = openai.OpenAI()

def init_session_state():
    import streamlit as st
    for key in ["questions", "answers"]:
        if key not in st.session_state:
            st.session_state[key] = []

def retrieve_relevant_clauses(query, mode):
    # Placeholder: implement with your actual FAISS or hybrid logic
    return [
        {
            "clause_number": "22",
            "title": "MDIO - Basic Management Interface",
            "text": "Clause 22 describes the basic two-wire serial management interface...",
            "applies_to": ["PHY", "MAC"],
            "functions": ["management", "configuration"],
            "related_clauses": ["45"]
        },
        {
            "clause_number": "45",
            "title": "MDIO - Extended Management Interface",
            "text": "Clause 45 extends Clause 22 for higher addressability and features...",
            "applies_to": ["PHY"],
            "functions": ["advanced management"],
            "related_clauses": ["22", "73"]
        }
    ]

def format_clause_context(clauses, mode):
    context = []
    for c in clauses:
        clause_str = f"Clause {c['clause_number']}: {c['title']}\n{c['text']}"
        context.append(clause_str)
    return "\n\n".join(context)

def get_openai_answer(question, clause_context, mode, clauses):
    messages = [
        {"role": "system", "content": f"You are a protocol assistant helping with {mode} queries. Include tradeoffs, caveats, and real-world context when possible."},
        {"role": "user", "content": f"{question}\n\nRelevant Clauses:\n{clause_context}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",  # GPT-4.1
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

def parse_sectioned_response(text):
    section_headers = ["Tradeoffs", "Caveats", "Real-World Context"]
    sections = {header: "" for header in section_headers}
    current = None

    for line in text.splitlines():
        line_strip = line.strip()
        if line_strip.rstrip(":") in section_headers:
            current = line_strip.rstrip(":")
        elif current:
            sections[current] += line + "\n"

    formatted = ""
    for header in section_headers:
        content = sections[header].strip()
        if content:
            formatted += f"**{header}:**\n\n{content}\n\n"
    return formatted.strip()

def export_chat_history_to_pdf(questions, answers):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for i, (q, a) in enumerate(zip(questions, answers), 1):
        pdf.set_text_color(0, 0, 255)
        pdf.multi_cell(0, 10, f"Q{i}: {q}")
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, f"A{i}: {a}")
        pdf.ln(5)

    filename = f"exports/siphy_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)

def save_query_history(question, answer, clauses):
    data = {
        "question": question,
        "answer": answer,
        "clauses": clauses,
        "timestamp": datetime.now().isoformat()
    }
    with open("query_log.jsonl", "a") as f:
        f.write(json.dumps(data) + "\n")
