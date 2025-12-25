import requests
from ddgs import DDGS

ACTIVE_API_KEY = None


def set_api_key(key):
    """Sets the Tavily API key for the session."""
    global ACTIVE_API_KEY
    if key and key.strip():
        ACTIVE_API_KEY = key.strip()
        print(f"🔑 [Adapter] API Key Activated: {ACTIVE_API_KEY[:5]}******")
    else:
        ACTIVE_API_KEY = None
        print("🔑 [Adapter] API Key Removed. Switched to Free Mode.")


def search_tavily(query):
    """Searches using the paid Tavily API."""
    print(f"🕵️ [Tavily] Searching via API: '{query}'...")
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": ACTIVE_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": 3
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if not results:
                return None

            context = ""
            for i, res in enumerate(results, 1):
                context += f"Source {i} ({res['title']}): {res['content']}\nLink: {res['url']}\n\n"
            return context

        elif response.status_code == 401:
            print("❌ [Tavily] Invalid Key! Falling back to Free Mode...")
            return None
        else:
            print(f"❌ [Tavily] Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ [Tavily] Connection Error: {e}")
        return None


def search_ddg(query):
    """Searches using DuckDuckGo (Free Mode)."""
    print(f"🦆 [DuckDuckGo] Searching Free Mode: '{query}'...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return None

        context = ""
        for i, res in enumerate(results, 1):
            context += f"Source {i} ({res['title']}): {res['body']}\nLink: {res['href']}\n\n"
        return context
    except Exception as e:
        print(f"❌ [DuckDuckGo] Error: {e}")
        return None


def search_web(query):
    """
    Main controller: Tries Tavily first, falls back to DuckDuckGo.
    """
    # Safety Guard
    if not query or len(query.strip()) < 3:
        print("⚠️ [Search] Query too short/empty. Skipping web search.")
        return None

    # 1. Try Tavily
    if ACTIVE_API_KEY and len(ACTIVE_API_KEY) > 5:
        result = search_tavily(query)
        if result:
            return result

    # 2. Fallback to DuckDuckGo
    print("⚠️ [Search] Using Fallback (Free Mode)")
    return search_ddg(query)
