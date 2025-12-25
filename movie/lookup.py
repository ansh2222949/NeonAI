import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web import search_adapter
from models import hybrid_llm

def fetch_movie_info(user_query, history):
    """
    Searches the web for specific movie details and summarizes them.
    Strictly used for information lookup, not recommendations.
    """
    print(f"🌐 [Movie Lookup] Analyzing query: '{user_query}'")
    
    # Optimize search query for better results
    search_query = f"{user_query} movie details rating reviews plot"
    
    print(f"🔍 [Movie Lookup] Sending to Search Adapter: '{search_query}'")
    
    web_data = search_adapter.search_web(search_query)
    
    if not web_data:
        print("❌ [Movie Lookup] No data found online.")
        return "🌐 [System]: I looked online, but I couldn't find reliable details for this movie."

    print("🧠 [Movie Lookup] Synthesizing answer with Hybrid LLM...")
    
    return hybrid_llm.generate_response(user_query, web_data, history)