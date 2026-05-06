import sqlite3
import sqlite_vec
from app.config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.DATABASE_URL.replace("sqlite:///", ""))
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Structured data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id TEXT PRIMARY KEY,
            file_url TEXT,
            photo_date TEXT,
            emotion TEXT,
            is_smiling INTEGER,
            is_crying INTEGER,
            activity TEXT,
            location_type TEXT,
            location_detail TEXT,
            people_count INTEGER,
            has_other_people INTEGER,
            clothing_description TEXT,
            hair_length TEXT,
            is_funny INTEGER,
            funniness_score INTEGER,
            cuteness_score INTEGER,
            objects TEXT, -- JSON string
            season_guess TEXT,
            description TEXT,
            uploaded_at TEXT,
            notes TEXT
        )
    ''')
    # Vector table for semantic search
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS photo_embeddings USING vec0(
            photo_id TEXT PRIMARY KEY,
            description_embedding float[768]
        )
    ''')
    conn.commit()
    conn.close()
