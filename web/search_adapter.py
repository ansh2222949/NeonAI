import requests
from ddgs import DDGS

ACTIVE_API_KEY = None


def set_api_key(key):
    global ACTIVE_API_KEY
    if key and key.strip():
        ACTIVE_API_KEY = key.strip()
        print(f"🔑 [Adapter] API Key Activated: {ACTIVE_API_KEY[:5]}******")
    else:
        ACTIVE_API_KEY = None
        print("🔑 [Adapter] API Key Removed. Switched to Free Mode.")


# =========================
# VERIFIED SEARCH (TAVILY)
# =========================
def search_tavily(query):
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

        if response.status_code != 200:
            print(f"❌ [Tavily] Error: {response.status_code}")
            return None

        results = response.json().get("results", [])
        if not results:
            return None

        context = "WEB SOURCES (VERIFIED):\n"
        for i, res in enumerate(results, 1):
            context += (
                f"[{i}] {res.get('title', 'Unknown Source')}\n"
                f"Summary: {res.get('content', '').strip()}\n"
                f"URL: {res.get('url', '')}\n"
                f"Credibility: Verified (Tavily API)\n\n"
            )

        return context

    except Exception as e:
        print(f"❌ [Tavily] Connection Error: {e}")
        return None


# =========================
# FREE SEARCH (DUCKDUCKGO)
# =========================
def search_ddg(query):
    print(f"🦆 [DuckDuckGo] Searching Free Mode: '{query}'...")

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return None

        context = "WEB SOURCES (UNVERIFIED):\n"
        for i, res in enumerate(results, 1):
            context += (
                f"[{i}] {res.get('title', 'Unknown Source')}\n"
                f"Summary: {res.get('body', '').strip()}\n"
                f"URL: {res.get('href', '')}\n"
                f"Credibility: Unverified (Free Web Search)\n\n"
            )

        return context

    except Exception as e:
        print(f"❌ [DuckDuckGo] Error: {e}")
        return None


# =========================
# MAIN CONTROLLER
# =========================
def search_web(query):
    if not query or len(query.strip()) < 3:
        print("⚠️ [Search] Query too short. Skipping web search.")
        return None

    # 1️⃣ Try verified search first
    if ACTIVE_API_KEY and len(ACTIVE_API_KEY) > 5:
        result = search_tavily(query)
        if result:
            return result

    # 2️⃣ Fallback to unverified free search
    print("⚠️ [Search] Falling back to Free Mode")
    return search_ddg(query)
