from models import local_llm
import re


def generate_response(user_text, web_data, history=None):
    """
    Formats Web Data + User Query into a strict grounded prompt.
    Uses run_raw_prompt to avoid double templating.
    """

    # -----------------------------
    # Safety Check
    # -----------------------------
    if not web_data or not web_data.strip():
        return "Not found."

    if history is None:
        history = []

    # -----------------------------
    # Format History (Clean + Limited)
    # -----------------------------
    history_str = ""

    if history:
        history_str = "\n--- CONVERSATION HISTORY ---\n"

        for msg in history[-5:]:  # Limit history to last 5 turns
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "").strip()
            history_str += f"{role}: {content}\n"

        history_str += "--- END HISTORY ---\n"

    # -----------------------------
    # Construct Strict Grounded Prompt
    # -----------------------------
    augmented_prompt = (
        "You are NeonAI.\n"
        "Answer STRICTLY using only the SEARCH RESULTS below.\n\n"
        "Rules:\n"
        "1. If the answer is not explicitly present, reply exactly: Not found.\n"
        "2. Do not explain anything.\n"
        "3. Do not add extra commentary.\n"
        "4. Do not mention limitations or the system.\n"
        "5. Respond in clear English only.\n\n"
        "--- SEARCH RESULTS ---\n"
        f"{web_data}\n"
        "--- END SEARCH RESULTS ---\n"
        f"{history_str}"
        f"User: {user_text}\n"
        "Assistant:"
    )

    # -----------------------------
    # Execute Raw Prompt
    # -----------------------------
    response = local_llm.run_raw_prompt(
        augmented_prompt,
        temperature=0.2
    )

    clean_response = response.strip()

    # -----------------------------
    # Extra Safety Guard
    # -----------------------------

    # If model tries to escape rules
    forbidden_patterns = [
        "as an ai",
        "i cannot",
        "i don't have access",
        "based on my knowledge",
        "according to my training"
    ]

    if any(p in clean_response.lower() for p in forbidden_patterns):
        return "Not found."

    # Force exact fallback format
    if not clean_response:
        return "Not found."

    # Prevent multi-paragraph rambling
    if len(clean_response.split("\n")) > 6:
        clean_response = "\n".join(clean_response.split("\n")[:6]).strip()

    return clean_response
