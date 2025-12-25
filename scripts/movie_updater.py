import sys
import os
import json
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web import search_adapter
from models import local_llm

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'movie', 'movie_db.json')
REQUIRED_KEYS = {"title", "year", "rating", "genre", "mood", "plot"}

def get_current_month_query():
    now = datetime.datetime.now()
    return f"Top movies released in {now.strftime('%B %Y')} with genre rating and plot"

def update_database():
    """
    Searches for new movies, parses details using LLM, and updates the local JSON database.
    """
    print("\n🛠️  [Admin Tool] Starting Database Maintenance...")
    print(f"📂 Target DB: {os.path.abspath(DB_PATH)}")
    
    # Search Web
    query = get_current_month_query()
    print(f"🌐 Searching: '{query}'...")
    
    web_data = search_adapter.search_web(query)
    
    if not web_data:
        print("❌ No data found online. Aborting update.")
        return

    # Parse data using LLM
    print("🧠 Parsing raw data into JSON structure...")
    
    prompt = (
        "Extract movie details from the text below and format as a JSON LIST.\n"
        "Strict Format: [{'title': 'Name', 'year': 2025, 'rating': 8.0, 'genre': ['Action'], 'mood': ['Exciting'], 'plot': 'Summary'}]\n"
        "Rules: Return ONLY valid JSON. No extra text.\n"
        "Ensure 'genre' and 'mood' are lists of strings.\n\n"
        f"--- TEXT DATA ---\n{web_data}"
    )
    
    json_str = local_llm.run_raw_prompt(prompt, temperature=0.1)
    
    try:
        # JSON Extraction & Cleanup
        start = json_str.find('[')
        end = json_str.rfind(']') + 1
        clean_json = json_str[start:end]
        
        raw_movies = json.loads(clean_json)
        
        if not raw_movies:
            print("⚠️ Parser returned empty list.")
            return

        # Validation Layer
        valid_movies = []
        for m in raw_movies:
            if not REQUIRED_KEYS.issubset(m.keys()):
                print(f"⚠️ Skipping Invalid Entry (Missing Keys): {m.get('title', 'Unknown')}")
                continue
            
            if not isinstance(m['genre'], list) or not isinstance(m['mood'], list):
                print(f"⚠️ Skipping Invalid Entry (Wrong Format): {m.get('title')}")
                continue

            valid_movies.append(m)

        if not valid_movies:
            print("❌ No valid movies found after validation.")
            return

        # Merge with Existing DB
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                old_db = json.load(f)
        else:
            old_db = []

        existing_titles = [m['title'].lower() for m in old_db]
        
        for movie in valid_movies:
            if movie['title'].lower() not in existing_titles:
                old_db.append(movie)
                print(f"✅ Added: {movie['title']}")
            else:
                print(f"ℹ️  Duplicate skipped: {movie['title']}")

        # Save Database
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(old_db, f, indent=4)
            
        print(f"\n🎉 Maintenance Complete! Database now has {len(old_db)} movies.")

    except json.JSONDecodeError:
        print("❌ Parsing Failed: LLM did not return valid JSON.")
    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    print("⚠️  Ensure Ollama (Server) is running for the Parser to work.")
    update_database()