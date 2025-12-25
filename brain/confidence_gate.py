import re

def validate_answer(ai_response, user_text=None):
    """
    Validates AI response to filter out refusals, weak answers, 
    or hallucinated real-time data.
    """
    response_lower = ai_response.lower().strip()

    # Check for explicit unknown token
    if "[[unknown]]" in response_lower:
        return "FALLBACK", None

    # check for weak or refusal phrases
    weak_phrases = [
        "i don't know", "i do not know", "i'm sorry", "i am sorry",
        "as an ai", "my knowledge cutoff", "not been released",
        "rumors suggest", "no official information", "unable to browse",
        "cannot provide", "real-time information"
    ]

    if any(phrase in response_lower for phrase in weak_phrases):
        return "FALLBACK", None

    # Check for real-time data hallucination (prices, scores, etc.)
    if user_text:
        user_lower = user_text.lower()
        realtime_words = [
            "price", "cost", "rate", "today", "current", 
            "latest", "won", "score", "weather"
        ]

        # If user asks for real-time info and AI gives a number, treat as unsafe
        if any(word in user_lower for word in realtime_words):
            if re.search(r"\d", response_lower):
                return "FALLBACK", None

    return "PASS", ai_response