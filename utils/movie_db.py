import sqlite3
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "neon_movies.db")
CACHE_DAYS = 7

def init_db():
    """Initializes the database table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            rating TEXT,
            plot TEXT,
            poster TEXT,
            cast TEXT,
            timestamp REAL
        )
    ''')
    
    conn.commit()
    conn.close()

def get_movie_from_db(query):
    """
    Retrieves movie from DB. Checks if cache is older than 7 days.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM movies WHERE title LIKE ?", ('%' + query + '%',))
        row = cursor.fetchone()
        conn.close()

        if row:
            saved_time = row[6] if len(row) > 6 else 0
            current_time = time.time()
            days_diff = (current_time - saved_time) / (24 * 3600)

            if days_diff > CACHE_DAYS:
                print(f"⚠️ [Database] Data for '{row[1]}' is old. Refreshing...")
                return None
            
            return {
                "title": row[1],
                "rating": row[2],
                "plot": row[3],
                "poster": row[4],
                "cast": row[5]
            }
        return None
        
    except Exception as e:
        print(f"❌ DB Read Error: {e}")
        return None

def save_movie_to_db(data):
    """Saves or updates movie data with current timestamp."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        current_time = time.time()
        
        cursor.execute('''
            REPLACE INTO movies (title, rating, plot, poster, cast, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['title'], data['rating'], data['plot'], data['poster'], data['cast'], current_time))
        
        conn.commit()
        conn.close()
        print(f"💾 [Database] Saved: {data['title']}")
        
    except Exception as e:
        print(f"❌ DB Save Error: {e}")

# Initialize table on import
init_db()