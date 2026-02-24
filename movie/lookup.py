import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web import search_adapter
from models import hybrid_llm
from utils import network


def fetch_movie_info(user_query, history=None):
    """
    Movie Lookup Engine (Production Ready)

    - Uses Web Search for factual movie data
    - Generates structured English output
    - Guards against weak search results
    - Internet-aware
    """

    # -----------------------------------------
    # 1️⃣ Input Validation
    # -----------------------------------------
    if not user_query or not isinstance(user_query, str):
        return "Invalid movie query."

    user_query = user_query.strip()

    if history is None:
        history = []

    # Limit history to avoid context overflow
    history = history[-5:]

    print(f"[Movie Lookup] Query: '{user_query}'")

    # -----------------------------------------
    # 2️⃣ Internet Guard
    # -----------------------------------------
    if not network.is_internet_allowed(mode="movie"):
        print("[Movie Lookup] Internet not available.")
        return "Internet access is unavailable."

    # -----------------------------------------
    # 3️⃣ Optimized Search Query
    # -----------------------------------------
    search_query = (
        f"{user_query} movie title cast rating release year "
        f"official plot summary director reviews"
    )

    print("[Movie Lookup] Sending to Search Adapter.")
    web_data = search_adapter.search_web(search_query)

    # -----------------------------------------
    # 4️⃣ Weak Search Filtering
    # -----------------------------------------
    if not web_data or not web_data.strip():
        print("[Movie Lookup] No data returned.")
        return "Movie details not found online."

    # If search result is too small, it's unreliable
    if len(web_data.strip()) < 200:
        print("[Movie Lookup] Weak search result detected.")
        return "Movie details not found online."

    # -----------------------------------------
    # 5️⃣ Structured Response Generation
    # -----------------------------------------
    print("[Movie Lookup] Generating structured response.")

    system_instruction = (
        "You are a factual movie information assistant.\n"
        "Generate a clean structured response with:\n"
        "- Title\n"
        "- Release Year\n"
        "- Rating\n"
        "- Director\n"
        "- Main Cast\n"
        "- Short Plot Summary\n"
        "Keep it strictly factual. No speculation."
    )

    response = hybrid_llm.generate_response(
        user_query=user_query,
        web_data=web_data,
        history=history,
        system_instruction=system_instruction
    )

    # -----------------------------------------
    # 6️⃣ Response Validation
    # -----------------------------------------
    if not response:
        print("[Movie Lookup] Empty response.")
        return "Movie details not found online."

    cleaned = response.strip()

    if cleaned.lower() in ["not found.", "not found", "unknown"]:
        return "Movie details not found online."

    # Prevent hallucination garbage
    if len(cleaned) < 50:
        return "Movie details not found online."

    return cleaned
