import sqlite3
import threading

class Database:
    def __init__(self, db_path="ads.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self.create_tables()

    def create_tables(self):
        with self.lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS ads (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    price INTEGER,
                    url TEXT,
                    location TEXT,
                    km TEXT,
                    year TEXT,
                    image_url TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY
                )
            """)
            self.conn.commit()

    def save_user(self, user_id):
        with self.lock:
            c = self.conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            self.conn.commit()

    def get_all_users(self):
        with self.lock:
            c = self.conn.cursor()
            c.execute("SELECT user_id FROM users")
            return [row[0] for row in c.fetchall()]

    def exists(self, ad_id):
        with self.lock:
            c = self.conn.cursor()
            c.execute("SELECT 1 FROM ads WHERE id = ?", (ad_id,))
            return c.fetchone() is not None

    def insert_ad(self, ad):
        with self.lock:
            c = self.conn.cursor()
            c.execute("""
                INSERT OR IGNORE INTO ads (id, title, price, url, location, km, year, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ad['id'], ad['title'], ad['price'], ad['url'], ad['location'], ad['km'], ad['year'], ad['image_url']))
            self.conn.commit()

    def get_stats(self):
        with self.lock:
            c = self.conn.cursor()
            c.execute("SELECT MIN(price), MAX(price), AVG(price) FROM ads")
            row = c.fetchone()
            if row:
                return {"min_price": row[0] or 0, "max_price": row[1] or 0, "avg_price": row[2] or 0}
            return None

