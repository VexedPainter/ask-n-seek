import sqlite3
import contextlib

DB_PATH = "ask_n_seek.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    with contextlib.closing(get_connection()) as conn:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    timestamp_s REAL NOT NULL,
                    class_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    color TEXT,
                    x1 INTEGER NOT NULL,
                    y1 INTEGER NOT NULL,
                    x2 INTEGER NOT NULL,
                    y2 INTEGER NOT NULL,
                    spatial_relation TEXT,
                    spatial_target_color TEXT
                )
            ''')

def insert_detections(detections_list):
    """
    detections_list: list of dicts with keys matching the columns
    """
    query = '''
        INSERT INTO detections (video_id, timestamp_s, class_name, confidence, color, x1, y1, x2, y2, spatial_relation, spatial_target_color)
        VALUES (:video_id, :timestamp_s, :class_name, :confidence, :color, :x1, :y1, :x2, :y2, :spatial_relation, :spatial_target_color)
    '''
    with contextlib.closing(get_connection()) as conn:
        with conn:
            conn.executemany(query, detections_list)
