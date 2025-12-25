from exam import retriever
from web import search_adapter, movie_adapter
from utils import network, movie_db
from brain import confidence_gate, memory
from models import local_llm, hybrid_llm
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


REALTIME_TRIGGERS = [
    "price", "cost", "how much", "latest", "news", "update",
    "today", "yesterday", "tomorrow", "release date", "launch date",
    "rumors", "specs", "features", "who won", "score", "vs",
    "weather", "forecast"
]


def execute_waterfall(user_text, mode="casual", context=None, history=None):
    if history is None:
        history = []

    print(f"\n🌊 [Waterfall] Mode: {mode} | Query: {user_text}")

    # --- EXAM MODE ---
    if mode == "exam":
        found_context = retriever.get_relevant_context(user_text)

        if not found_context:
            return "Out of Syllabus."

        return local_llm.run_inference(
            user_text,
            mode="exam",
            context=found_context,
            history=history
        )

    # --- MOVIE MODE ---
    elif mode == "movie":
        local_data = movie_db.get_movie_from_db(user_text)

        if local_data:
            response = (
                f"🎬 **Title:** {local_data['title']}\n"
                f"⭐ **Rating:** {local_data['rating']}/10\n"
                f"🎭 **Cast:** {local_data['cast']}\n\n"
                f"📝 **Plot:** {local_data['plot']}"
            )
            if local_data['poster']:
                response += f"\n\n[Poster: {local_data['poster']}]"
            return response

        # Not in DB, try Online
        if network.is_internet_allowed(mode="movie"):
            tmdb_data = movie_adapter.get_online_movie(user_text)

            if tmdb_data:
                movie_db.save_movie_to_db(tmdb_data)

                response = (
                    f"🎬 **Title:** {tmdb_data['title']}\n"
                    f"⭐ **Rating:** {tmdb_data['rating']}/10\n"
                    f"🎭 **Cast:** {tmdb_data['cast']}\n\n"
                    f"📝 **Plot:** {tmdb_data['plot']}"
                )
                if tmdb_data['poster']:
                    response += f"\n\n[Poster: {tmdb_data['poster']}]"
                return response
            else:
                return "Sorry, I couldn't find that movie on TMDB."
        else:
            return "Movie not found in local database and Internet is disabled."

    # --- CASUAL MODE ---
    else:
        is_realtime_query = any(trigger in user_text.lower()
                                for trigger in REALTIME_TRIGGERS)

        if is_realtime_query:
            if network.is_internet_allowed(mode="casual"):
                web_results = search_adapter.search_web(user_text)
                if not web_results:
                    return "Not found online."
                return hybrid_llm.generate_response(user_text, web_results, history)
            else:
                return "This requires internet, but network is unavailable."

        # Try Local Brain First
        local_response = local_llm.run_inference(
            user_text, mode="casual", history=history)
        status, clean_response = confidence_gate.validate_answer(
            local_response, user_text=user_text)

        if status == "PASS":
            return clean_response

        # Fallback to Internet
        if network.is_internet_allowed(mode="casual"):
            web_results = search_adapter.search_web(user_text)
            if not web_results:
                return "Not found online."
            return hybrid_llm.generate_response(user_text, web_results, history)
        else:
            return "I don't know this, and Internet is unavailable."
