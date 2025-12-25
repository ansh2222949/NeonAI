from web import search_adapter, movie_adapter
from exam import indexer
from brain import waterfall, memory
import os
import re
import sys
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pyngrok import ngrok

# --- SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
WALLPAPER_DIR = os.path.join(STATIC_DIR, 'wallpapers')

os.makedirs(WALLPAPER_DIR, exist_ok=True)
sys.path.append(BASE_DIR)


app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, resources={r"/*": {"origins": "*"}})

CHAT_HISTORY = []
MAX_HISTORY = 10
USER_FACTS = {}

# --- HELPERS ---


def sanitize_english(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'[\u0900-\u097F]+', '', text)
    hindi_fillers = [r"\bnamaste\b", r"\bhaan\b", r"\bnahi\b", r"\baccha\b"]
    for word in hindi_fillers:
        text = re.sub(word, "", text, flags=re.IGNORECASE)
    return text.strip()

# --- ROUTES ---


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/upload-bg", methods=["POST"])
def upload_bg():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No selected file"}), 400

    try:
        filepath = os.path.join(WALLPAPER_DIR, "current_bg.jpg")
        file.save(filepath)
        return jsonify({"status": "success", "url": "/static/wallpapers/current_bg.jpg"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No selected file"}), 400

    try:
        upload_dir = os.path.join("exam", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, "syllabus.pdf")
        file.save(filepath)

        success, msg = indexer.process_pdf("syllabus.pdf")
        status = "success" if success else "error"
        return jsonify({"status": status, "message": msg})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500


@app.route("/delete-pdf", methods=["POST"])
def delete_pdf_endpoint():
    try:
        pdf_path = os.path.join("exam", "uploads", "syllabus.pdf")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            return jsonify({"status": "success", "message": "PDF Deleted."})
        return jsonify({"status": "error", "message": "No PDF found."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/reset-exam-db", methods=["POST"])
def reset_exam_db_endpoint():
    try:
        success, msg = indexer.clear_database()
        status = "success" if success else "error"
        return jsonify({"status": status, "message": msg})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/set-api-key", methods=["POST"])
def set_api_key_endpoint():
    try:
        data = request.json
        api_key = data.get("api_key", "").strip()
        search_adapter.set_api_key(api_key)
        msg = "Tavily Key Activated! 🚀" if api_key else "Using Free Search Mode."
        return jsonify({"status": "success", "message": msg})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/set-tmdb-key", methods=["POST"])
def set_tmdb_key_endpoint():
    try:
        data = request.json
        api_key = data.get("api_key", "").strip()
        movie_adapter.set_api_key(api_key)
        msg = "Movie Mode Activated! 🎬" if api_key else "TMDB Key Removed. Offline Only."
        return jsonify({"status": "success", "message": msg})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    global CHAT_HISTORY, USER_FACTS
    try:
        data = request.json
        user_text = data.get("message", "").strip()
        mode = data.get("mode", "casual")

        if not user_text:
            return jsonify({"error": "Empty message"}), 400

        print(f"\n📥 INPUT | Mode={mode} | Text='{user_text}'")
        clean_lower = user_text.lower()

        # Movie Preference Learning
        if mode != "exam" and ("i like" in clean_lower or "i love" in clean_lower):
            genres = ["action", "sci-fi", "comedy", "horror",
                      "drama", "romance", "adventure", "thriller"]
            detected = [g for g in genres if g in clean_lower]
            if detected:
                for g in detected:
                    memory.update_preference(g)
                reply = f"I've noted that you like {', '.join(detected)} movies."
                return jsonify({"response": reply, "mode_used": "preference_learning"})

        # Memory Recall
        if "my name is" in clean_lower:
            match = re.search(r"my name is\s+(\w+)", clean_lower)
            if match:
                name = match.group(1).capitalize()
                USER_FACTS["name"] = name
                return jsonify({"response": f"Got it! I'll call you {name}.", "mode_used": "memory_learn"})

        if any(q in clean_lower for q in ["who am i", "what is my name"]):
            if "name" in USER_FACTS:
                return jsonify({"response": f"Your name is {USER_FACTS['name']}.", "mode_used": "memory_recall"})
            return jsonify({"response": "I don't know your name yet.", "mode_used": "memory_fail"})

        # Waterfall Execution
        raw_response = waterfall.execute_waterfall(
            user_text, mode=mode, history=CHAT_HISTORY)
        final_response = sanitize_english(raw_response)

        CHAT_HISTORY.append({"role": "user", "content": user_text})
        CHAT_HISTORY.append({"role": "assistant", "content": final_response})
        if len(CHAT_HISTORY) > MAX_HISTORY:
            CHAT_HISTORY = CHAT_HISTORY[-MAX_HISTORY:]

        return jsonify({"response": final_response, "mode_used": mode})

    except Exception as e:
        print("❌ SERVER ERROR:", e)
        return jsonify({"error": "Internal Brain Error. Check logs."}), 500


@app.route("/reset", methods=["POST"])
def reset():
    global CHAT_HISTORY
    CHAT_HISTORY = []
    return jsonify({"status": "Conversation reset successfully."})

# --- MAIN EXECUTION ---


if __name__ == "__main__":
    # IMPORTANT: Set these in Environment Variables for GitHub safety
    NGROK_TOKEN = os.environ.get("NGROK_AUTH_TOKEN")
    STATIC_DOMAIN = os.environ.get("NGROK_STATIC_DOMAIN")

    print("---------------------------------------------------")
    print("🚀 NeonAI V3 Server Starting...")

    # Attempt Ngrok Connection (Optional)
    if NGROK_TOKEN and STATIC_DOMAIN:
        try:
            ngrok.set_auth_token(NGROK_TOKEN)
            public_url = ngrok.connect(5000, domain=STATIC_DOMAIN).public_url
            print(f"🌍 PUBLIC STATIC URL: {public_url}")
        except Exception as e:
            print(f"⚠️ Ngrok Error: {e}")
            print("⚠️ Running in Local Mode")
    else:
        print("ℹ️  Ngrok Token not found. Running Locally.")

    print("🏠 Local URL: http://localhost:5000")
    print("---------------------------------------------------")

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
