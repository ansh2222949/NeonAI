import json
import os
from typing import Dict


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")


def _get_profile_path(mode: str) -> str:
    """
    Returns separate profile file path per mode.
    """
    safe_mode = mode.lower().strip()
    return os.path.join(USER_DATA_DIR, f"{safe_mode}_profile.json")


def load_profile(mode: str = "general") -> Dict:
    """
    Loads user profile from JSON based on mode.
    Each mode has completely isolated memory.
    """

    profile_path = _get_profile_path(mode)

    if not os.path.exists(profile_path):
        return {
            "name": "User",
            "favorite_genres": [],
            "watched": [],
            "mode": mode
        }

    try:
        with open(profile_path, 'r', encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "name": "User",
            "favorite_genres": [],
            "watched": [],
            "mode": mode
        }


def save_profile(data: Dict, mode: str = "general") -> None:
    """
    Saves user profile to JSON based on mode.
    """

    profile_path = _get_profile_path(mode)

    try:
        os.makedirs(USER_DATA_DIR, exist_ok=True)

        with open(profile_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"Memory Save Error: {e}")


def update_preference(genre: str, mode: str = "movie") -> bool:
    """
    Adds a genre to favorites for a specific mode.
    Default mode = movie (since genres are movie related).
    """

    profile = load_profile(mode)

    current_favs = [g.lower() for g in profile.get("favorite_genres", [])]

    if genre.lower().strip() not in current_favs:
        profile.setdefault("favorite_genres", []).append(genre.capitalize())
        save_profile(profile, mode)
        return True

    return False


def get_favorites(mode: str = "movie"):
    """
    Returns favorite genres for a specific mode.
    """

    profile = load_profile(mode)
    return profile.get("favorite_genres", [])
