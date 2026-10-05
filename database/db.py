import sqlite3
import os
from config import Config

def get_db_connection(db_path=None):
    if db_path is None:
        db_path = Config.DATABASE_PATH
    
    # Auto-initialize if file does not exist
    need_init = not os.path.exists(db_path) or os.path.getsize(db_path) == 0
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if need_init:
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
    return conn

def init_db(db_path=None):
    if db_path is None:
        db_path = Config.DATABASE_PATH
    
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    conn = get_db_connection(db_path)
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()

def get_or_create_default_user(db_path=None):
    """Ensures a default user (id=1) exists in database."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = 1")
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO users (id) VALUES (1)")
            conn.commit()
        return 1
    finally:
        conn.close()
