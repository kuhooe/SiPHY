# 📝 clause_feedback.py — Save Clause Ratings & Freeform Feedback

import os
import json
from datetime import datetime

# 💾 Feedback File Path
FEEDBACK_FILE = "feedback/feedback_log.json"

# 📁 Ensure feedback directory and file exist
def init_feedback_file():
    os.makedirs("feedback", exist_ok=True)
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

# 👍 Structured Feedback from Clause Buttons (Rating + Query)
def save_clause_feedback(clause_number, query, rating, feedback_text=None):
    init_feedback_file()
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "clause": clause_number,
        "question": query,
        "rating": rating
    }
    if feedback_text:
        entry["feedback"] = feedback_text
    try:
        with open(FEEDBACK_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error saving feedback:", e)

# ✍️ Optional Freeform Text Feedback (Optional extension UI)
def record_feedback(clause_number, feedback_text, rating, user_query):
    init_feedback_file()
    feedback_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "clause": clause_number,
        "rating": rating,
        "feedback": feedback_text,
        "query": user_query
    }
    try:
        with open(FEEDBACK_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(feedback_entry)
            f.seek(0)
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error saving text feedback:", e)

# 🧾 Save Query History for PDF export
def save_query_history(question, answer, clauses, filename="query_history.json"):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer,
        "clauses": clauses
    }

    try:
        with open(filename, "r", encoding="utf-8") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(entry)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
