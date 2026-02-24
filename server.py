from web import search_adapter, movie_adapter
from exam import indexer
from brain import waterfall, memory
import os
import re
import sys
import time  # 1️⃣ Added time module
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pyngrok import ngrok


# -----------------------------
# SETUP
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
WALLPAPER_DIR = os.path.join(STATIC_DIR, 'wallpapers')

os.makedirs(WALLPAPER_DIR, exist_ok=True)
sys.path.append(BASE_DIR)

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, resources={r"/*": {"origins": "*"}})

# 2️⃣ MEMORY ISOLATION (Per Mode)
# Instead of one big list, we separate them so contexts don't mix.
HISTORY = {
    "casual": [],
    "exam": [],
    "movie": [],
    "coding": []
}

MAX_HISTORY = 10
USER_FACTS = {}

ALLOWED_MODES = {"casual", "exam", "movie", "coding"}


# -----------------------------
# HELPERS
# -----------------------------

def sanitize_english(text: str) -> str:
    """
    Cleans output while strictly preserving newlines and indentation.
    """
    if not text:
        return ""

    # Remove Devanagari only
    text = re.sub(r'[\u0900-\u097F]+', '', text)

    # Remove Hindi fillers (line safe)
    hindi_fillers = [
        r"\bnamaste\b", r"\bhaan\b", r"\bnahi\b", r"\baccha\b"
    ]

    for word in hindi_fillers:
        text = re.sub(word, "", text, flags=re.IGNORECASE)

    # 🔥 DO NOT collapse whitespace
    lines = text.split("\n")
    cleaned = [line.rstrip() for line in lines]

    return "\n".join(cleaned).strip()


def enforce_code_formatting(text: str, mode: str) -> str:
    """
    Ensures coding mode responses are properly formatted.
    """
    if mode != "coding":
        return text

    if "```" not in text:
        text = f"```python\n{text}\n```"

    inside = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", text)

    if inside:
        code = inside[0]
        code = re.sub(r"\s+(?=(def |class |for |while |if |elif |else:|print\(|return |# ))", "\n", code)
        code = re.sub(r"(\w+\s*=\s*[^#\n]+)\s+(?=\w+\s*=)", r"\1\n", code)
        text = f"```python\n{code.strip()}\n```"

    return text


def detect_pure_math(text: str) -> bool:
    """
    Detects simple mathematical expressions like 5 + 7.
    """
    if not text:
        return False
    text = text.strip()
    pattern = r"^\d+(\.\d+)?\s*[\+\-\*/]\s*\d+(\.\d+)?$"
    return bool(re.fullmatch(pattern, text))


def detect_coding_intent(text: str) -> bool:
    """
    Smart detection for coding-related queries.
    """
    if not text:
        return False

    text_lower = text.lower()

    languages = ["python", "java", "c++", "javascript", "html", "css", "sql", "c#", "go", "rust"]
    if any(lang in text_lower for lang in languages):
        return True

    structure_patterns = [
        r"\bdef\s+\w+\(", r"\bclass\s+\w+", r"\bfor\s+\w+\s+in\s+",
        r"\bwhile\s+.*:", r"\bif\s+.*:", r"print\(", r"\w+\s*=\s*.+"
    ]
    for pattern in structure_patterns:
        if re.search(pattern, text):
            return True

    operator_pattern = r"\d+\s*[\+\-\*/]\s*\d+"
    if re.search(operator_pattern, text):
        return True

    symbol_pattern = r"[{}();]"
    if re.search(symbol_pattern, text):
        return True

    return False


# -----------------------------
# ROUTES
# -----------------------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/upload-bg", methods=["POST"])
def upload_bg():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"status": "error", "message": "Empty filename"}), 400
    try:
        filepath = os.path.join(WALLPAPER_DIR, "current_bg.jpg")
        file.save(filepath)
        return jsonify({"status": "success", "url": "/static/wallpapers/current_bg.jpg"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"status": "error", "message": "Empty filename"}), 400
    try:
        upload_dir = os.path.join("exam", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, "syllabus.pdf")
        file.save(filepath)
        success, msg = indexer.process_pdf("syllabus.pdf")
        return jsonify({"status": "success" if success else "error", "message": msg})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/reset-exam-db", methods=["POST"])
def reset_exam_db_endpoint():
    try:
        success, msg = indexer.clear_database()
        return jsonify({"status": "success" if success else "error", "message": msg})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/set-api-key", methods=["POST"])
def set_api_key_endpoint():
    try:
        data = request.get_json(silent=True) or {}
        api_key = data.get("api_key", "").strip()
        search_adapter.set_api_key(api_key)
        message = "Verified search enabled." if api_key else "Using free search mode."
        return jsonify({"status": "success", "message": message})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/set-tmdb-key", methods=["POST"])
def set_tmdb_key_endpoint():
    try:
        data = request.get_json(silent=True) or {}
        api_key = data.get("api_key", "").strip()
        movie_adapter.set_api_key(api_key)
        message = "Movie online mode enabled." if api_key else "TMDB key removed."
        return jsonify({"status": "success", "message": message})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    global HISTORY, USER_FACTS  # Using the dictionary now

    # 3️⃣ Start Timer
    start_time = time.time()

    try:
        data = request.get_json(silent=True) or {}
        user_text = data.get("message", "").strip()
        mode = data.get("mode", "casual").lower().strip()

        if not user_text:
            return jsonify({"error": "Empty message"}), 400

        if mode not in ALLOWED_MODES:
            return jsonify({"error": "Invalid mode"}), 400

        clean_lower = user_text.lower()

        # --- LEVEL 2 INTELLIGENCE ---

        # 1. Pure Math
        if mode == "casual" and detect_pure_math(user_text):
            try:
                result = eval(user_text)
                print(f"🧮 Pure Math: {user_text} = {result}")
                
                # Calculate time even for direct math
                response_time = round(time.time() - start_time, 3)
                print(f"⚡ Route: math_direct | Time: {response_time}s")

                return jsonify({
                    "response": str(result),
                    "mode_used": "math_direct",
                    "mode": mode,
                    "response_time": response_time
                })
            except:
                pass

        # 2. Smart Coding Switch
        if mode == "casual" and detect_coding_intent(user_text):
            print(f"⚙️ Smart Switch: casual -> coding")
            mode = "coding"

        # --- MEMORY OPERATIONS ---
        if mode != "exam" and ("i like" in clean_lower or "i love" in clean_lower):
            genres = ["action", "sci-fi", "comedy", "horror", "drama", "romance", "adventure", "thriller"]
            detected = [g for g in genres if g in clean_lower]
            if detected:
                for g in detected:
                    memory.update_preference(g, mode="movie")
                
                response_time = round(time.time() - start_time, 3)
                return jsonify({
                    "response": f"I have noted that you like {', '.join(detected)} movies.",
                    "mode_used": "preference_learning",
                    "response_time": response_time
                })

        # Name Logic
        if "my name is" in clean_lower:
            match = re.search(r"my name is\s+(\w+)", clean_lower)
            if match:
                name = match.group(1).capitalize()
                USER_FACTS["name"] = name
                response_time = round(time.time() - start_time, 3)
                return jsonify({
                    "response": f"I will call you {name}.",
                    "mode_used": "memory_learn",
                    "response_time": response_time
                })

        if any(q in clean_lower for q in ["who am i", "what is my name"]):
            response_time = round(time.time() - start_time, 3)
            if "name" in USER_FACTS:
                return jsonify({
                    "response": f"Your name is {USER_FACTS['name']}.",
                    "mode_used": "memory_recall",
                    "response_time": response_time
                })
            return jsonify({
                "response": "I do not know your name yet.",
                "mode_used": "memory_fail",
                "response_time": response_time
            })

        # --- WATERFALL EXECUTION ---
        # 4️⃣ Pass Isolated History based on Mode
        current_history = HISTORY[mode]

        raw_response = waterfall.execute_waterfall(
            user_text,
            mode=mode,
            history=current_history  # Only passing specific history
        )

        final_response = sanitize_english(raw_response)

        if mode == "coding":
            final_response = enforce_code_formatting(final_response, mode)

        # 5️⃣ Update Isolated History
        HISTORY[mode].append({"role": "user", "content": user_text})
        HISTORY[mode].append({"role": "assistant", "content": final_response})

        if len(HISTORY[mode]) > MAX_HISTORY:
            HISTORY[mode] = HISTORY[mode][-MAX_HISTORY:]

        # 6️⃣ Calculate Time & Log
        response_time = round(time.time() - start_time, 3)
        print(f"⚡ Route: {mode} | Time: {response_time}s")

        return jsonify({
            "response": final_response,
            "mode_used": mode,
            "mode": mode,
            "response_time": response_time  # Return to frontend
        })

    except Exception as e:
        print("[SERVER ERROR]", e)
        return jsonify({"error": "Internal server error."}), 500


@app.route("/reset", methods=["POST"])
def reset():
    global HISTORY
    # Reset all modes
    HISTORY = {
        "casual": [],
        "exam": [],
        "movie": [],
        "coding": []
    }
    return jsonify({"status": "All conversation memories cleared."})


# -----------------------------
# MAIN EXECUTION
# -----------------------------

if __name__ == "__main__":
    # Aise likhein
    NGROK_TOKEN = ""
    STATIC_DOMAIN = ""

    print("---------------------------------------------------")
    print("NeonAI Server Starting (Level 3 Intelligence)")
    print("---------------------------------------------------")

    if NGROK_TOKEN and STATIC_DOMAIN:
        try:
            ngrok.set_auth_token(NGROK_TOKEN)
            public_url = ngrok.connect(5000, domain=STATIC_DOMAIN).public_url
            print(f"Public URL: {public_url}")
        except Exception as e:
            print(f"Ngrok Error: {e}")
            print("Running in Local Mode.")
    else:
        print("Ngrok not configured. Running locally.")

    print("Local URL: http://localhost:5000")
    print("---------------------------------------------------")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )