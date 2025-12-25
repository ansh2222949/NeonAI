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
    Cleans output to ensure pure English and removes Hindi artifacts.
    """
    if not text:
        return ""

    # Remove Devanagari script
    text = re.sub(r'[\u0900-\u097F]+', '', text)

    # Remove specific Hindi conversational fillers
    hindi_words = [
        "namaste", "haan", "nahi", "kya", "kaise",
        "bhai", "tum", "aap", "accha", "theek"
    ]
    for w in hindi_words:
        text = re.sub(rf"\b{w}\b", "", text, flags=re.IGNORECASE)

    # Normalize spaces
    return re.sub(r'\s+', ' ', text).strip()

def build_prompt(user_text, mode="casual", context=None, history=None):
    """Constructs the prompt based on mode and history."""
    if history is None:
        history = []

    history_str = ""
    if history:
        history_str = "\n--- CONVERSATION HISTORY ---\n"
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"
        history_str += "--- END HISTORY ---\n"

    if mode == "casual":
        system = (
            "You are NeonAI, a helpful assistant.\n"
            "LANGUAGE RULE (NON-NEGOTIABLE):\n"
            "- Reply ONLY in pure English.\n"
            "- Do NOT use Hindi, Hinglish, or Roman Hindi.\n"
            "- Do NOT use Devanagari script.\n"
            "- Keep responses clear, short, kind and calm.\n"
            "- Your owner name is Ansh.\n"
        )
        return f"System: {system}\n{history_str}\nUser: {user_text}\nAssistant:"

    if mode == "exam":
        system = (
            "You are a strict Exam Tutor.\n"
            "Answer ONLY using the provided Context.\n"
            "CRITICAL RULE: If the answer is NOT in the context, reply EXACTLY:\n"
            "Out of Syllabus.\n"
            "Reply ONLY in pure English."
        )
        return f"System: {system}\nContext: {context}\n{history_str}\nUser: {user_text}\nAssistant:"

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
            "stop": ["User:", "System:"]
        }
    }
    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=60)
        return res.json().get("response", "").strip()
    except requests.RequestException as e:
        return f"Brain Error: {e}"

def run_inference(user_text, mode="casual", context=None, history=None):
    """Standard inference wrapper."""
    if not connect_ollama():
        return "Error: Ollama is not running."

    prompt = build_prompt(user_text, mode, context, history)
    temperature = 0.6 if mode == "casual" else 0.1

    raw_output = _execute_ollama(prompt, temperature)
    return sanitize_output(raw_output)

def run_raw_prompt(raw_prompt, temperature=0.3):
    """Executes a raw prompt string (used for Hybrid/Web modes)."""
    if not connect_ollama():
        return "Error: Ollama is not running."

    raw_output = _execute_ollama(raw_prompt, temperature)
    return sanitize_output(raw_output)