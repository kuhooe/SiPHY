# ethernet_bot.py — Core Clause Assistant Logic (Finalized for 3 Modes)

from utils import (
    retrieve_relevant_clauses,
    format_clause_context,
    get_openai_answer
)

# Generate Answer for Ethernet Query
def answer_ethernet_query(question, mode):
    clauses = retrieve_relevant_clauses(question, mode)

    if mode == "Expert":
        context = clauses
    else:
        context = format_clause_context(clauses, mode)

    answer = get_openai_answer(question, context, mode)

    # 🔧 Add design disclaimer
    if mode in ["Smart Designer", "Expert"]:
        disclaimer = (
            "⚠️ *Note: This response is based solely on Ethernet protocol standards and known behavior patterns. "
            "Since SiPHY does not have access to your specific design or environment, this answer reflects general principles, not your exact system.*\n\n"
        )
        answer = disclaimer + answer

    # 🔧 Fix response labeling
    if mode == "Smart Designer":
        answer = f"**Smart Designer Mode Response**\n\n{answer}"
    elif mode == "Expert":
        sources = "\n".join(f"- Clause {c['clause_id']}: {c['title']}" for c in clauses)
        answer = f"**Expert Context Mode Response**\n\n{answer}\n\n**Citations**\n\n{sources}"
    elif mode == "Strict Clause Lookup":
        answer = f"**Strict Clause Lookup Mode Response**\n\n{answer}"
      
    except Exception:
        return "OpenAI failed to answer the query.", clauses

    return answer, clauses

