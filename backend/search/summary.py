import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.db.schema import get_connection

def get_top_objects(video_id: str, limit: int = 10):
    """
    Returns list of top objects for a video by count.
    Each item: {class_name, count, avg_confidence, dominant_color}
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Get classes by count and avg confidence
    query = """
        SELECT class_name, COUNT(*) as c, AVG(confidence) as avg_conf
        FROM detections
        WHERE video_id = ?
        GROUP BY class_name
        ORDER BY c DESC
        LIMIT ?
    """
    cursor.execute(query, (video_id, limit))
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        class_name = row['class_name']
        count = row['c']
        avg_conf = row['avg_conf']
        
        # 2. Get dominant color for this class
        color_query = """
            SELECT color, COUNT(*) as cc
            FROM detections
            WHERE video_id = ? AND class_name = ? AND color IS NOT NULL
            GROUP BY color
            ORDER BY cc DESC
            LIMIT 1
        """
        cursor.execute(color_query, (video_id, class_name))
        color_row = cursor.fetchone()
        dominant_color = color_row['color'] if color_row else None
        
        results.append({
            "class_name": class_name,
            "count": count,
            "avg_confidence": round(avg_conf, 2),
            "dominant_color": dominant_color
        })
        
    conn.close()
    return results
