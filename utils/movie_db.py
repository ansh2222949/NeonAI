import sqlite3
import time
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "neon_movies.db")
CACHE_DAYS = 7


def _get_connection():
    """
    Returns a safe SQLite connection with performance settings.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_db():
    """Initializes the database table if it doesn't exist."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE COLLATE NOCASE,
            rating TEXT,
            plot TEXT,
            poster TEXT,
            cast TEXT,
            timestamp REAL
        )
    ''')

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON movies(title);")

    conn.commit()
    conn.close()


def get_movie_from_db(query):
    """
    Retrieves movie from DB.
    Returns None if cache expired or not found.
    """

    if not query:
        return None

    try:
        conn = _get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT title, rating, plot, poster, cast, timestamp "
            "FROM movies WHERE title LIKE ? COLLATE NOCASE LIMIT 1",
            ('%' + query.strip() + '%',)
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        title, rating, plot, poster, cast, saved_time = row

        current_time = time.time()
        days_diff = (current_time - saved_time) / (24 * 3600)

        if days_diff > CACHE_DAYS:
            print(f"[Database] Cache expired for '{title}'.")
            return None

        return {
            "title": title,
            "rating": rating,
            "plot": plot,
            "poster": poster,
            "cast": cast
        }

    except Exception as e:
        print(f"[Database] Read error: {e}")
        return None


def save_movie_to_db(data):
    """
    Saves or updates movie data with current timestamp.
    """

    if not isinstance(data, dict):
        return

    required_fields = ["title", "rating", "plot", "poster", "cast"]

    if not all(field in data for field in required_fields):
        print("[Database] Invalid movie data format.")
        return

    try:
        conn = _get_connection()
        cursor = conn.cursor()

        current_time = time.time()

        cursor.execute('''
            INSERT INTO movies (title, rating, plot, poster, cast, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(title) DO UPDATE SET
                rating=excluded.rating,
                plot=excluded.plot,
                poster=excluded.poster,
                cast=excluded.cast,
                timestamp=excluded.timestamp
        ''', (
            data["title"],
            data["rating"],
            data["plot"],
            data["poster"],
            data["cast"],
            current_time
        ))

        conn.commit()
        conn.close()

        print(f"[Database] Saved or updated: {data['title']}")

    except Exception as e:
        print(f"[Database] Save error: {e}")


# Initialize table on import
init_db()
