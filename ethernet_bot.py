# ✅ ethernet_bot.py — Core Clause Assistant Logic (Restored and Repaired)

from utils import (
    retrieve_relevant_clauses,
    format_clause_context,
    get_openai_answer
)

# Generate Answer for Ethernet Query
def answer_ethernet_query(question, mode):
    try:
        # Get relevant clauses and format context
        clauses = retrieve_relevant_clauses(question, mode)
        if mode.lower() == "expert":
            context = clauses  # expert mode can handle raw clause objects
        else:
            context = format_clause_context(clauses, mode)

        # Generate base answer
        answer = get_openai_answer(question, context, mode)

        # ⚠️ Insert disclaimer if needed
        if "smart designer" in mode.lower() or "expert" in mode.lower():
            disclaimer = (
                "⚠️ *Note: This response is based solely on Ethernet protocol standards and known behavior patterns. "
                "Since SiPHY does not have access to your specific design or environment, this answer reflects general principles, not your exact system.*\n\n"
            )
            answer = disclaimer + answer

        # 🏷️ Add response label (once)
        if "smart designer" in mode.lower():
            answer = f"**Smart Designer Mode Response**\n\n{answer}"
        elif "expert" in mode.lower():
            answer = f"**Expert Context Mode Response**\n\n{answer}\n\n_Disclaimer: Interpretive response. Always verify with clause data._"
        elif "strict" in mode.lower():
            answer = f"**Strict Clause Lookup Mode Response**\n\n{answer}"

        return answer, clauses

    except Exception:
        return "OpenAI failed to answer the query.", []
