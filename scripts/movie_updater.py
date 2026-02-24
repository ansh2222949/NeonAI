import sys
import os
import json
import datetime
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web import search_adapter
from models import local_llm

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'movie', 'movie_db.json')
REQUIRED_KEYS = {"title", "year", "rating", "genre", "mood", "plot"}

def get_current_month_query():
    now = datetime.datetime.now()
    return f"Top movies released in {now.strftime('%B %Y')} with genre rating and plot"

def _safe_extract_json(text: str):
    """
    Extract first valid JSON list safely using positional indexing.
    """
    if not text:
        return None

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end <= start:
        return None

    candidate = text[start:end + 1]

    try:
        json.loads(candidate) # Validate structure
        return candidate
    except Exception:
        return None

def update_database():
    """
    Searches for new movies, parses details using LLM,
    validates them, and safely updates the local JSON database.
    """

    print("\n[Admin Tool] Starting Database Maintenance...")
    
    # -----------------------------
    # 1. Web Search
    # -----------------------------
    query = get_current_month_query()
    print(f"[Admin Tool] Searching: '{query}'")
    web_data = search_adapter.search_web(query)

    if not web_data or not web_data.strip():
        print("[Admin Tool] No data found online. Aborting.")
        return

    # -----------------------------
    # 2. LLM JSON Parsing
    # -----------------------------
    print("[Admin Tool] Parsing raw data into JSON structure...")
    prompt = (
        "Extract movie details from the text below and format as a JSON LIST.\n"
        "Strict format example:\n"
        "[{\"title\": \"Name\", \"year\": 2025, \"rating\": 8.0, "
        "\"genre\": [\"Action\"], \"mood\": [\"Exciting\"], \"plot\": \"Summary\"}]\n"
        "Rules:\n"
        "- Return ONLY valid JSON.\n"
        "- Rating must be 0.0 to 10.0.\n"
        "- Genre and mood must be lists of strings.\n\n"
        f"--- TEXT DATA ---\n{web_data}"
    )

    json_str = local_llm.run_raw_prompt(prompt, temperature=0.05)
    clean_json = _safe_extract_json(json_str)

    if not clean_json:
        print("[Admin Tool] Parsing failed. No valid JSON array detected.")
        return

    try:
        raw_movies = json.loads(clean_json)
    except json.JSONDecodeError:
        print("[Admin Tool] JSON decoding failed.")
        return

    # -----------------------------
    # 3. Validation & Normalization Layer
    # -----------------------------
    valid_movies = []
    current_year = datetime.datetime.now().year

    for m in raw_movies:
        if not isinstance(m, dict) or not REQUIRED_KEYS.issubset(m.keys()):
            continue

        try:
            # Type & Range Validation
            is_valid_year = isinstance(m["year"], int) and (1900 <= m["year"] <= current_year + 1)
            is_valid_rating = isinstance(m["rating"], (int, float)) and (0 <= m["rating"] <= 10)
            is_valid_lists = isinstance(m["genre"], list) and isinstance(m["mood"], list)

            if not (is_valid_year and is_valid_rating and is_valid_lists):
                print(f"[Admin Tool] Skipping invalid data for: {m.get('title')}")
                continue

            # Normalization (Strip whitespace and Title Case)
            m["genre"] = [g.strip().title() for g in m["genre"] if isinstance(g, str)]
            m["mood"] = [md.strip().title() for md in m["mood"] if isinstance(md, str)]
            
            valid_movies.append(m)
        except Exception as e:
            print(f"[Admin Tool] Error validating {m.get('title')}: {e}")

    if not valid_movies:
        print("[Admin Tool] No valid movies passed validation.")
        return

    # -----------------------------
    # 4. Merge & Backup Logic
    # -----------------------------
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    old_db = []
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                old_db = json.load(f)
                # CREATE BACKUP
                with open(DB_PATH + ".backup", 'w', encoding='utf-8') as bf:
                    json.dump(old_db, bf, indent=4)
        except Exception:
            old_db = []

    existing_titles = {m.get("title", "").lower() for m in old_db}
    added_count = 0

    for movie in valid_movies:
        title_lower = movie["title"].lower()
        if title_lower not in existing_titles:
            old_db.append(movie)
            existing_titles.add(title_lower)
            added_count += 1
            print(f"[Admin Tool] Added: {movie['title']}")

    # -----------------------------
    # 5. Atomic-style Save
    # -----------------------------
    try:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(old_db, f, indent=4)
        print(f"\n[Admin Tool] Update complete. New movies: {added_count} | Total: {len(old_db)}")
    except Exception as e:
        print(f"[Admin Tool] Critical save error: {e}")

if __name__ == "__main__":
    update_database()