# ethernet_bot.py — Core Clause Assistant Logic (Finalized for 3 Modes)

from utils import (
    retrieve_relevant_clauses,
    format_clause_context,
    get_openai_answer
)

# Generate Answer for Ethernet Query
def answer_ethernet_query(query, mode):
    clauses = retrieve_relevant_clauses(query, mode)

    if not clauses:
        return "No relevant clauses found.", []

    clause_context = format_clause_context(clauses, mode)

    try:
        answer = get_openai_answer(query, clause_context, mode)

        # Add response labels and citations based on mode
        if mode == "Smart Designer":
            answer = f"**Smart Designer Mode Response**\n\n{answer}"
        elif mode == "Expert Context Mode":
            sources = "\n".join(f"- Clause {c['clause_id']}: {c['title']}" for c in clauses)
            answer = f"**Expert Context Mode Response**\n\n{answer}\n\n**Citations**\n\n{sources}"
        elif mode == "Strict Clause Lookup":
            answer = f"**Strict Clause Lookup Mode Response**\n\n{answer}"

    except Exception:
        return "OpenAI failed to answer the query.", clauses

    return answer, clauses
