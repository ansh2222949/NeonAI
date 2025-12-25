import requests

TMDB_API_KEY = None


def set_api_key(key):
    """Sets the TMDB API key globally."""
    global TMDB_API_KEY
    TMDB_API_KEY = key


def get_online_movie(query):
    """
    Searches TMDB for a movie and returns formatted details.
    """
    if not TMDB_API_KEY:
        print("⚠️ [TMDB] No API Key provided.")
        return None

    try:
        # Search for the movie
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        response = requests.get(search_url).json()

        if not response.get('results'):
            return None

        # Process the top result
        movie = response['results'][0]
        movie_id = movie['id']

        # Fetch detailed info + credits
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
        details = requests.get(details_url).json()

        # Extract specific data
        cast_list = [actor['name'] for actor in details['credits']['cast'][:3]]
        poster_path = movie.get('poster_path')
        full_poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

        return {
            "title": movie['title'],
            "rating": str(round(movie['vote_average'], 1)),
            "plot": movie['overview'],
            "poster": full_poster,
            "cast": ", ".join(cast_list),
            "release_date": movie['release_date']
        }

    except Exception as e:
        print(f"❌ [TMDB Error] {e}")
        return None
