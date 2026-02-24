import requests
import re

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


def connect_ollama():
    """Checks if Ollama server is running."""
    try:
        r = requests.get("http://localhost:11434/", timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False


def sanitize_output(text: str) -> str:
    """
    Cleans output while preserving code formatting, indentation, and newlines.
    """
    if not text:
        return ""

    # Remove Devanagari script
    text = re.sub(r'[\u0900-\u097F]+', '', text)

    # Remove common Hindi fillers
    hindi_words = [
        "namaste", "haan", "nahi", "kya", "kaise",
        "bhai", "tum", "aap", "accha", "theek"
    ]

    for w in hindi_words:
        text = re.sub(rf"\b{w}\b", "", text, flags=re.IGNORECASE)

    # Remove accidental system leakage (line safe)
    text = re.sub(r"^System:.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^User:.*$", "", text, flags=re.MULTILINE)

    # 🔥 IMPORTANT: Preserve newlines and indentation
    lines = text.split("\n")
    
    # We only strip trailing spaces (rstrip). 
    cleaned_lines = [line.rstrip() for line in lines]

    return "\n".join(cleaned_lines).strip()


def enforce_code_formatting(text: str, mode: str) -> str:
    """
    Ensures coding mode responses are properly formatted.
    Auto-fixes single-line compressed code as a safety net.
    """

    if mode != "coding":
        return text

    # If no code block exists but it looks like code, wrap everything
    if "```" not in text:
        text = f"```python\n{text}\n```"

    # Try fixing compressed Python statements inside code blocks
    inside = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", text)

    if inside:
        code = inside[0]

        # Insert newline before common Python keywords if missing
        code = re.sub(r"\s+(?=(def |class |for |while |if |elif |else:|print\(|return |# ))", "\n", code)

        # Ensure assignments split (e.g. "a=1 b=2" -> "a=1\nb=2")
        code = re.sub(r"(\w+\s*=\s*[^#\n]+)\s+(?=\w+\s*=)", r"\1\n", code)

        text = f"```python\n{code.strip()}\n```"

    return text


def build_prompt(user_text, mode="casual", context=None, history=None):
    """Constructs the prompt based on mode and history."""

    if history is None:
        history = []

    # Limit history for stability
    history = history[-5:]

    history_str = ""
    if history:
        history_str = "\n--- CONVERSATION HISTORY ---\n"
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"
        history_str += "--- END HISTORY ---\n"

    # ============================
    # CASUAL MODE
    # ============================
    if mode == "casual":
        system = (
            "You are NeonAI, a helpful assistant.\n"
            "Language rule (strict): Reply only in pure English.\n"
            "Keep responses clear and concise.\n"
            "Do not use Hindi or mixed language.\n"
            "Owner name: Ansh.\n"
        )
        return f"System: {system}\n{history_str}\nUser: {user_text}\nAssistant:"

    # ============================
    # EXAM MODE
    # ============================
    if mode == "exam":
        system = (
            "You are a strict Exam Tutor.\n"
            "Answer ONLY using the provided Context.\n"
            "If the answer is not found in the context, reply exactly:\n"
            "Out of Syllabus.\n"
            "Reply in pure English only.\n"
        )
        return (
            f"System: {system}\n"
            f"Context:\n{context}\n"
            f"{history_str}\n"
            f"User: {user_text}\nAssistant:"
        )

    # ============================
    # CODING MODE (🔥 PROFESSIONAL & STRICT)
    # ============================
    if mode == "coding":
        system = (
            "You are a strict professional Python coding assistant.\n"
            "\n"
            "CRITICAL FORMAT RULES:\n"
            "1. Output ONLY code.\n"
            "2. Wrap ALL code inside triple backticks.\n"
            "3. Every statement MUST be on its own line.\n"
            "4. Use proper indentation (4 spaces).\n"
            "5. Never write multiple statements on one line.\n"
            "6. Never compress code.\n"
            "7. Never explain unless explicitly asked.\n"
            "\n"
            "If the format rules are violated, regenerate internally before answering.\n"
        )
        return f"System: {system}\n{history_str}\nUser: {user_text}\nAssistant:"

    # ============================
    # MOVIE MODE
    # ============================
    if mode == "movie":
        system = (
            "You are a movie expert assistant.\n"
            "Explain clearly in English.\n"
            "Never output raw JSON.\n"
            "Provide structured information only.\n"
        )
        return f"System: {system}\n{history_str}\nUser: {user_text}\nAssistant:"

    return user_text


def _execute_ollama(prompt, temperature):
    """Internal function to send request to Ollama."""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": 4096,
            "stop": ["User:", "System:", "--- END HISTORY ---"]
        }
    }

    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=90)
        data = res.json()

        if "response" not in data:
            return "Model response error."

        return data["response"].strip()

    except requests.RequestException as e:
        return f"Brain Error: {e}"


def run_inference(user_text, mode="casual", context=None, history=None):
    """Standard inference wrapper."""

    if not connect_ollama():
        return "Error: Ollama is not running."

    prompt = build_prompt(user_text, mode, context, history)

    # Temperature Control Per Mode
    if mode == "casual":
        temperature = 0.6
    elif mode == "coding":
        # 🔥 ZERO TEMPERATURE: Forces the model to be deterministic and structured.
        temperature = 0.0
    elif mode == "exam":
        temperature = 0.0
    elif mode == "movie":
        temperature = 0.3
    else:
        temperature = 0.4

    raw_output = _execute_ollama(prompt, temperature)
    
    # 🔥 Step 1: Basic cleaning
    cleaned = sanitize_output(raw_output)
    
    # 🔥 Step 2: Enforce formatting specifically for Coding Mode
    return enforce_code_formatting(cleaned, mode)


def run_raw_prompt(raw_prompt, temperature=0.3):
    """Executes a raw prompt string (used for Hybrid/Web modes)."""

    if not connect_ollama():
        return "Error: Ollama is not running."

    raw_output = _execute_ollama(raw_prompt, temperature)
    return sanitize_output(raw_output)