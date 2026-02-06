import sqlite3
import string
import random
from typing import Optional
from app.config import DATABASE_NAME, SHORT_CODE_LENGTH, logger


class Database:
    """Handle all database operations"""
    
    def __init__(self, db_name: str = DATABASE_NAME):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        """Create database connection"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def generate_short_code(self) -> str:
        """Generate unique short code"""
        characters = string.ascii_letters + string.digits
        
        while True:
            code = ''.join(random.choices(characters, k=SHORT_CODE_LENGTH))
            if not self.get_original_url(code):
                return code
    
    def create_short_url(self, original_url: str, custom_code: Optional[str] = None) -> str:
        """Create new short URL entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use custom code or generate new one
        short_code = custom_code if custom_code else self.generate_short_code()
        
        try:
            cursor.execute(
                "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
                (short_code, original_url)
            )
            conn.commit()
            logger.info(f"Created short URL: {short_code} -> {original_url}")
            return short_code
        except sqlite3.IntegrityError:
            logger.error(f"Short code {short_code} already exists")
            raise ValueError("Short code already exists")
        finally:
            conn.close()
    
    def get_original_url(self, short_code: str) -> Optional[str]:
        """Get original URL by short code"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT original_url FROM urls WHERE short_code = ?",
            (short_code,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result['original_url'] if result else None
    
    def increment_clicks(self, short_code: str):
        """Increment click counter for URL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
            (short_code,)
        )
        
        conn.commit()
        conn.close()
        logger.info(f"Incremented clicks for {short_code}")
    
    def delete_url(self, short_code: str) -> bool:
        """Delete URL by short code (bonus feature)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if deleted:
            logger.info(f"Deleted short URL: {short_code}")
        
        return deleted
    
    def get_stats(self, short_code: str) -> Optional[dict]:
        """Get statistics for URL (bonus feature)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM urls WHERE short_code = ?",
            (short_code,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None