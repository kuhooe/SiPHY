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
    if "smart designer" in mode.lower() or "expert" in mode.lower():
        disclaimer = (
            "\u26a0\ufe0f *Note: This response is based solely on Ethernet protocol standards and known behavior patterns. "
            "Since SiPHY does not have access to your specific design or environment, this answer reflects general principles, not your exact system.*\n\n"
        )
        answer = disclaimer + answer

    # 🔧 Fix response labeling
    if "smart designer" in mode.lower():
        answer = f"**Smart Designer Mode Response**\n\n{answer}"
    elif "expert" in mode.lower():
        sources = "\n".join(f"- Clause {c['clause_id']}: {c['title']}" for c in clauses)
        answer = f"**Expert Context Mode Response**\n\n{answer}\n\n**Citations**\n\n{sources}"
    elif "strict" in mode.lower():
        answer = f"**Strict Clause Lookup Mode Response**\n\n{answer}"
        
    except Exception:
        return "OpenAI failed to answer the query.", clauses

    return answer, clauses

