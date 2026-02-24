import requests
import re

TMDB_API_KEY = None
BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"


def set_api_key(key):
    """Sets the TMDB API key globally."""
    global TMDB_API_KEY
    TMDB_API_KEY = key.strip() if key else None


def _safe_request(url, timeout=8):
    """
    Performs safe HTTP request with timeout and status validation.
    """
    try:
        response = requests.get(url, timeout=timeout)

        if response.status_code != 200:
            return None

        return response.json()

    except requests.RequestException:
        return None


def _clean_query(query: str):
    """
    Cleans query to prevent malformed URL issues.
    """
    return re.sub(r"\s+", " ", query.strip())


def get_online_movie(query):
    """
    Searches TMDB for a movie and returns structured movie details.
    Returns None if not found or error occurs.
    """

    if not TMDB_API_KEY:
        print("[TMDB] API key not set.")
        return None

    if not query or not isinstance(query, str):
        return None

    query = _clean_query(query)

    # ---------------------------------
    # Search Movie
    # ---------------------------------
    search_url = (
        f"{BASE_URL}/search/movie"
        f"?api_key={TMDB_API_KEY}"
        f"&query={query}"
    )

    search_data = _safe_request(search_url)

    if not search_data or not search_data.get("results"):
        return None

    movie = search_data["results"][0]
    movie_id = movie.get("id")

    if not movie_id:
        return None

    # ---------------------------------
    # Fetch Details + Credits
    # ---------------------------------
    details_url = (
        f"{BASE_URL}/movie/{movie_id}"
        f"?api_key={TMDB_API_KEY}"
        f"&append_to_response=credits"
    )

    details = _safe_request(details_url)

    if not details:
        return None

    # ---------------------------------
    # Extract Fields Safely
    # ---------------------------------
    title = movie.get("title", "Unknown")

    vote = movie.get("vote_average")
    rating = str(round(vote, 1)) if isinstance(vote, (int, float)) else "N/A"

    plot = movie.get("overview") or "No description available."

    release_date = movie.get("release_date", "")
    year = release_date.split("-")[0] if release_date else "N/A"

    poster_path = movie.get("poster_path")
    full_poster = f"{POSTER_BASE}{poster_path}" if poster_path else ""

    cast_data = details.get("credits", {}).get("cast", [])
    cast_list = []

    for actor in cast_data[:5]:
        name = actor.get("name")
        if name:
            cast_list.append(name)

    cast = ", ".join(cast_list) if cast_list else "Not available"

    # ---------------------------------
    # Structured Return
    # ---------------------------------
    return {
        "title": title,
        "year": year,
        "rating": rating,
        "plot": plot,
        "poster": full_poster,
        "cast": cast
    }
