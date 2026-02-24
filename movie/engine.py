import json
import os
import random

DB_PATH = os.path.join(os.path.dirname(__file__), 'movie_db.json')

def load_db():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, Exception):
        return []

def recommend(user_query, user_favorites=None):
    """
    Level 4 Recommendation Engine: Weighted Scoring & Precision Matching.
    Fixed: Variable scope, Normalized ratings, and Threshold filtering.
    """
    movies = load_db()
    if not movies:
        return "Movie database is empty."

    # Convert favorites to set for O(1) intersection
    user_favorites_set = set(f.lower() for f in (user_favorites or []))
    query_lower = user_query.lower().strip()
    query_words = set(query_lower.split())
    
    scored_matches = []

    # 1. MOOD MAP (Supports multi-word detection)
    mood_map = {
        "emotional": ["drama", "romance", "sad", "tearjerker"],
        "feel good": ["comedy", "animation", "family", "happy"],
        "dark": ["thriller", "horror", "crime", "mystery", "gritty"],
        "exciting": ["action", "adventure", "sci-fi", "intense"]
    }

    # 2. RANKING ENGINE (Scoring Loop)
    for movie in movies:
        score = 0
        m_genres = set(g.lower() for g in movie.get("genre", []))
        m_moods = set(m.lower() for m in movie.get("mood", []))
        m_title_words = set(movie.get("title", "").lower().split())
        
        # A. Direct Keyword Match (+5)
        if query_words.intersection(m_genres | m_moods | m_title_words):
            score += 5

        # B. Phrase-based Mood Match (+4)
        for mood, related_genres in mood_map.items():
            if mood in query_lower:
                if m_genres.intersection(related_genres):
                    score += 4

        # C. User Preference Alignment (+3)
        if user_favorites_set.intersection(m_genres):
            score += 3

        # D. Quality Weight (Normalized: Rating * 0.3)
        # 10/10 movie gives +3 points. This prevents rating from overriding intent.
        rating = movie.get("rating", 0)
        score += (rating * 0.3) 

        # E. Threshold Filter
        # Minimum score of 4 ensures the movie is actually relevant to the query/mood.
        if score >= 4:
            scored_matches.append((score, movie))

    if not scored_matches:
        return "I couldn't find a specific match. Try a mood like 'dark' or 'feel good'!"

    # 3. SORT & SELECTION
    # Sort by Score (Primary) and Rating (Secondary)
    scored_matches.sort(key=lambda x: (x[0], x[1].get("rating", 0)), reverse=True)
    
    # Selection: Shuffle top 5 candidates to provide variety
    top_candidates = [item[1] for item in scored_matches[:5]]
    random.shuffle(top_candidates)
    final_selection = top_candidates[:3]

    # 4. FORMAT OUTPUT (Bug-Fixed Loop)
    intros = [
        "Based on your vibe, these films stand out:",
        "These movies match your taste perfectly:",
        "I think you'd really appreciate these:"
    ]
    
    response_lines = [random.choice(intros), ""]

    for m in final_selection:
        title = m.get("title", "Unknown")
        year = m.get("year", "N/A")
        rating = m.get("rating", "N/A")
        genre_list = m.get("genre", [])
        genre_str = ", ".join(genre_list)
        plot = m.get("plot", "No description available.")
        
        # Correctly re-calculate intersection for THIS specific movie
        current_m_genres = set(g.lower() for g in genre_list)
        common = current_m_genres.intersection(user_favorites_set)
        
        reason = ""
        if common:
            reason = f"\n\n💡 *Why this matches: Aligns with your interest in {', '.join(common)}.*"

        block = (
            f"🎬 **{title} ({year})**\n"
            f"⭐ {rating}/10\n"
            f"🎭 {genre_str}\n"
            f"📖 {plot}{reason}"
        )
        response_lines.append(block)
        response_lines.append("---")

    return "\n".join(response_lines).strip()