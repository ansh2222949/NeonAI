import requests
import re
from ddgs import DDGS


ACTIVE_API_KEY = None
MAX_RESULTS = 3
MAX_SUMMARY_LENGTH = 800


def set_api_key(key):
    global ACTIVE_API_KEY

    if key and key.strip():
        ACTIVE_API_KEY = key.strip()
        masked = ACTIVE_API_KEY[:4] + "******"
        print(f"[Search Adapter] API Key Activated: {masked}")
    else:
        ACTIVE_API_KEY = None
        print("[Search Adapter] API Key Removed. Using free mode.")


# -----------------------------------------
# Utility Functions
# -----------------------------------------

def _clean_text(text):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()[:MAX_SUMMARY_LENGTH]


def _sanitize_query(query):
    return re.sub(r"\s+", " ", query.strip())


# =========================
# VERIFIED SEARCH (TAVILY)
# =========================

def search_tavily(query, silent=False):

    query = _sanitize_query(query)

    if not silent:
        print(f"[Tavily] Searching: '{query}'")

    url = "https://api.tavily.com/search"

    payload = {
        "api_key": ACTIVE_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": MAX_RESULTS
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code != 200:
            if not silent:
                print(f"[Tavily] HTTP Error: {response.status_code}")
            return None

        data = response.json()
        results = data.get("results", [])

        if not results:
            return None

        context_lines = ["WEB SOURCES (VERIFIED):\n"]

        for i, res in enumerate(results, 1):
            title = _clean_text(res.get("title", "Unknown Source"))
            summary = _clean_text(res.get("content", ""))
            url_link = res.get("url", "")

            block = (
                f"[{i}] {title}\n"
                f"Summary: {summary}\n"
                f"URL: {url_link}\n"
                f"Credibility: Verified\n"
            )

            context_lines.append(block)

        return "\n".join(context_lines).strip()

    except requests.RequestException as e:
        if not silent:
            print(f"[Tavily] Connection Error: {e}")
        return None


# =========================
# FREE SEARCH (DUCKDUCKGO)
# =========================

def search_ddg(query, silent=False):

    query = _sanitize_query(query)

    if not silent:
        print(f"[DuckDuckGo] Searching: '{query}'")

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=MAX_RESULTS))

        if not results:
            return None

        context_lines = ["WEB SOURCES (UNVERIFIED):\n"]

        for i, res in enumerate(results, 1):
            title = _clean_text(res.get("title", "Unknown Source"))
            summary = _clean_text(res.get("body", ""))
            url_link = res.get("href", "")

            block = (
                f"[{i}] {title}\n"
                f"Summary: {summary}\n"
                f"URL: {url_link}\n"
                f"Credibility: Unverified\n"
            )

            context_lines.append(block)

        return "\n".join(context_lines).strip()

    except Exception as e:
        if not silent:
            print(f"[DuckDuckGo] Error: {e}")
        return None


# =========================
# MAIN CONTROLLER
# =========================

def search_web(query, silent=False):

    if not query or len(query.strip()) < 3:
        if not silent:
            print("[Search] Query too short. Skipping search.")
        return None

    query = _sanitize_query(query)

    # 1️⃣ Try verified search first
    if ACTIVE_API_KEY and len(ACTIVE_API_KEY) > 5:
        result = search_tavily(query, silent=silent)
        if result:
            return result

    # 2️⃣ Fallback to free search
    if not silent:
        print("[Search] Falling back to free search.")

    return search_ddg(query, silent=silent)
