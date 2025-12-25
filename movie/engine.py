import json
import os
import random

DB_PATH = os.path.join(os.path.dirname(__file__), 'movie_db.json')


def load_db():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def recommend(user_query, user_favorites=None):
    """
    Offline Recommendation Engine.
    Filters movies based on User Favorites or specific keywords.
    """
    movies = load_db()
    if not movies:
        return "❌ Movie Database is empty."

    if user_favorites is None:
        user_favorites = []

    query_lower = user_query.lower()
    matches = []

    # Check for generic intent ("suggest movie") + Favorites
    is_generic_query = (
        ("suggest" in query_lower or "recommend" in query_lower or "watch" in query_lower)
        and len(user_query.split()) < 6
    )

    if is_generic_query and user_favorites:
        for movie in movies:
            if any(fav.lower() in [g.lower() for g in movie['genre']] for fav in user_favorites):
                matches.append(movie)

    # Standard Keyword Search if no matches found yet
    if not matches:
        for movie in movies:
            attributes = movie['genre'] + movie['mood'] + [movie['title']]
            if any(attr.lower() in query_lower for attr in attributes):
                matches.append(movie)

    # Handle No Matches
    if not matches:
        if user_favorites:
            return (f"🚫 I couldn't find movies matching your query, and nothing in our DB matches your favorites "
                    f"({', '.join(user_favorites)}) yet. Try updating the DB!")
        return "🚫 No matches found. Tell me 'I like Action' so I can learn your taste!"

    # Format Output
    response = "🎬 **Recommendations:**\n\n"
    if is_generic_query and user_favorites:
        response = f"🎬 **Because you like {', '.join(user_favorites)}:**\n\n"

    random.shuffle(matches)

    for m in matches[:3]:
        response += (
            f"🎥 **{m['title']}** ({m['year']})\n"
            f"⭐ {m['rating']} | 🎭 {', '.join(m['genre'])}\n"
            f"📝 {m['plot']}\n\n"
        )
    return response.strip()


def get_local_info(movie_name):
    """Retrieves specific movie info locally."""
    movies = load_db()
    for m in movies:
        if m['title'].lower() in movie_name.lower():
            return (
                f"📂 **Local Data Found:**\n"
                f"🎥 {m['title']} ({m['year']})\n"
                f"⭐ Rating: {m['rating']}/10\n"
                f"📝 Plot: {m['plot']}"
            )
    return None
