from models import local_llm

def generate_response(user_text, web_data, history=None):
    """
    Formats Web Data + User Query into a single prompt.
    Uses run_raw_prompt to avoid double templating.
    """
    
    # Safety Check
    if not web_data or not web_data.strip():
        return "🌐 [System]: I couldn't find reliable information online."

    if history is None:
        history = []

    # Format History
    history_str = ""
    if history:
        history_str = "\n--- CONVERSATION HISTORY ---\n"
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"
        history_str += "--- END HISTORY ---\n"

    # Construct Strict Prompt
    augmented_prompt = (
        "System: You are NeonAI.\n"
        "You MUST answer ONLY using the SEARCH RESULTS provided below.\n\n"
        "CRITICAL RULES:\n"
        "1. If the answer is NOT found in the search results, reply with EXACTLY:\n"
        "\"Not found.\"\n"
        "2. Do NOT explain why.\n"
        "3. Do NOT mention the assistant, system, limitations, or access.\n"
        "4. Do NOT add any extra text.\n\n"
        "--- SEARCH RESULTS ---\n"
        f"{web_data}\n"
        "--- END SEARCH RESULTS ---\n"
        f"{history_str}\n"
        f"User: {user_text}\n"
        "Assistant:"
    )

    # Execute Raw Prompt
    response = local_llm.run_raw_prompt(
        augmented_prompt,
        temperature=0.3
    )

    return response.strip()