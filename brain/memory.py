import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_PATH = os.path.join(BASE_DIR, "user_data", "profile.json")


def load_profile():
    """Loads user profile from JSON."""
    if not os.path.exists(PROFILE_PATH):
        return {"name": "User", "favorite_genres": [], "watched": []}

    try:
        with open(PROFILE_PATH, 'r') as f:
            return json.load(f)
    except:
        return {"name": "User", "favorite_genres": [], "watched": []}


def save_profile(data):
    """Saves user profile to JSON."""
    try:
        os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
        with open(PROFILE_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Memory Save Error: {e}")


def update_preference(genre):
    """Adds a genre to favorites if not already present."""
    profile = load_profile()

    current_favs = [g.lower() for g in profile['favorite_genres']]

    if genre.lower() not in current_favs:
        profile['favorite_genres'].append(genre.capitalize())
        save_profile(profile)
        return True

    return False


def get_favorites():
    """Returns list of favorite genres."""
    profile = load_profile()
    return profile.get('favorite_genres', [])
