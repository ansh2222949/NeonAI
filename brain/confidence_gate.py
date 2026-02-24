import re

def validate_answer(ai_response, user_text=None, mode=None):
    """
    Validates AI response to filter out:
    - refusals
    - weak answers
    - hallucinated real-time data
    - raw JSON dumping (movie mode)
    - non-markdown code (coding mode)
    """

    response_lower = ai_response.lower().strip()

    # Check for explicit unknown token
    if "[[unknown]]" in response_lower:
        return "FALLBACK", None

    # Weak / refusal phrases
    weak_phrases = [
        "i don't know", "i do not know", "i'm sorry", "i am sorry",
        "as an ai", "my knowledge cutoff", "not been released",
        "rumors suggest", "no official information", "unable to browse",
        "cannot provide", "real-time information"
    ]

    if any(phrase in response_lower for phrase in weak_phrases):
        return "FALLBACK", None

    # -------------------------------
    # Real-time hallucination check
    # -------------------------------
    if user_text:
        user_lower = user_text.lower()
        realtime_words = [
            "price", "cost", "rate", "today", "current",
            "latest", "won", "score", "weather"
        ]

        if any(word in user_lower for word in realtime_words):
            if re.search(r"\d", response_lower):
                return "FALLBACK", None

    # -------------------------------
    # Coding Mode Validation
    # -------------------------------
    if mode == "coding":
        # Must return markdown code block
        if not re.search(r"```[\s\S]*?```", ai_response):
            return "FALLBACK", None

    # -------------------------------
    # Movie Mode Validation
    # -------------------------------
    if mode == "movie":
        # Block raw JSON dumping
        if re.search(r'^\s*{.*}\s*$', ai_response, re.DOTALL):
            return "FALLBACK", None

        # Must contain structured explanation keywords
        required_keywords = ["summary", "rating", "poster"]
        if not any(keyword in response_lower for keyword in required_keywords):
            return "FALLBACK", None

    # -------------------------------
    # Basic English Enforcement
    # -------------------------------
    # Block Hindi characters
    if re.search(r'[\u0900-\u097F]', ai_response):
        return "FALLBACK", None

    return "PASS", ai_response
