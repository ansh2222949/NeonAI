from exam import retriever
from web import search_adapter, movie_adapter
from utils import network, movie_db
from brain import confidence_gate, memory
from models import local_llm, hybrid_llm
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Expanded Triggers for switching to hybrid/web search
REALTIME_TRIGGERS = [
    "price", "cost", "how much", "latest", "news", "update",
    "today", "yesterday", "tomorrow", "release date", "launch date",
    "rumors", "specs", "features", "who won", "score", "vs",
    "weather", "forecast", "box office", "collection", "earnings"
]

def execute_waterfall(user_text, mode="casual", context=None, history=None):
    """
    Orchestrates the flow of intelligence based on mode and query intent.
    """
    if history is None:
        history = []

    print(f"\n[Waterfall] Mode: {mode} | Query: {user_text}")

    try:
        # =====================================================
        # 1. EXAM MODE (RAG based Isolation)
        # =====================================================
        if mode == "exam":
            found_context = retriever.get_relevant_context(user_text)

            if not found_context:
                return "Out of syllabus."

            response = local_llm.run_inference(
                user_text,
                mode="exam",
                context=found_context,
                history=history
            )

            status, clean = confidence_gate.validate_answer(
                response,
                user_text=user_text,
                mode="exam"
            )

            return clean if status == "PASS" else "Unable to generate valid exam response."

        # =====================================================
        # 2. MOVIE MODE (Cinematic Narrative Logic)
        # =====================================================
        elif mode == "movie":
            # Step A: Fetch Movie Data (Local first, then Online)
            movie_facts = movie_db.get_movie_from_db(user_text)

            if not movie_facts and network.is_internet_allowed(mode="movie"):
                tmdb_data = movie_adapter.get_online_movie(user_text)
                if tmdb_data:
                    movie_db.save_movie_to_db(tmdb_data)
                    movie_facts = tmdb_data

            if movie_facts:
                # Step B: Build clean structured context (No Markdown/Emojis)
                context_data = _build_movie_context(movie_facts)
                
                # Step C: LLM generates the beautiful cinematic output
                cinematic_response = local_llm.run_inference(
                    user_text,
                    mode="movie",
                    context=context_data, 
                    history=history
                )

                # Step D: Validation
                status, clean = confidence_gate.validate_answer(
                    cinematic_response,
                    user_text=user_text,
                    mode="movie"
                )
                
                if status == "PASS":
                    return clean

                # Step E: Fallback - Clean structured output if LLM fails
                rating = movie_facts.get('rating', 'N/A')
                return (
                    f"🎬 Title: {movie_facts.get('title', 'Unknown')}\n"
                    f"⭐ Rating: {round(rating, 1) if isinstance(rating, (int, float)) else rating}/10\n"
                    f"🎭 Cast: {movie_facts.get('cast', 'Not available')}\n\n"
                    f"📖 Story:\n{movie_facts.get('plot', 'No description available.')}"
                )

            return "Movie not found in database or online."

        # =====================================================
        # 3. CASUAL MODE (Hybrid Search + Local Brain)
        # =====================================================
        else:
            is_realtime_query = any(
                trigger in user_text.lower()
                for trigger in REALTIME_TRIGGERS
            )

            if is_realtime_query:
                if network.is_internet_allowed(mode="casual"):
                    web_results = search_adapter.search_web(user_text)
                    if not web_results:
                        return "Not found online."

                    return hybrid_llm.generate_response(
                        user_text,
                        web_results,
                        history
                    )
                return "This requires internet, but network is unavailable."

            local_response = local_llm.run_inference(
                user_text,
                mode="casual",
                history=history
            )

            status, clean_response = confidence_gate.validate_answer(
                local_response,
                user_text=user_text,
                mode="casual"
            )

            if status == "PASS":
                return clean_response

            if network.is_internet_allowed(mode="casual"):
                web_results = search_adapter.search_web(user_text)
                if not web_results:
                    return "Not found online."

                return hybrid_llm.generate_response(
                    user_text,
                    web_results,
                    history
                )

            return "Unable to answer and internet is unavailable."

    except Exception as e:
        traceback.print_exc()
        return "Internal system error."

# =====================================================
# HELPERS
# =====================================================

def _build_movie_context(data):
    """
    Converts raw movie DB data into clean structured context for LLM.
    Pure facts, no formatting.
    """
    return (
        f"Title: {data.get('title', 'Unknown')}\n"
        f"Rating: {data.get('rating', 'N/A')}\n"
        f"Release Year: {data.get('year', 'Unknown')}\n"
        f"Genre: {data.get('genre', 'Unknown')}\n"
        f"Director: {data.get('director', 'Unknown')}\n"
        f"Cast: {data.get('cast', 'Not available')}\n"
        f"Plot: {data.get('plot', 'No description available.')}\n"
        f"Poster: {data.get('poster', 'Not available')}\n"
    )