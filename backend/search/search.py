import sqlite3
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.db.schema import get_connection

def build_search_query(filter_dict, video_id):
    query_parts = [
        "SELECT ROUND(timestamp_s) as window, COUNT(*) as det_count, MAX(confidence) as max_conf, GROUP_CONCAT(x1 || ',' || y1 || ',' || x2 || ',' || y2, ';') as bboxes",
        "FROM detections",
        "WHERE video_id = ?"
    ]
    params = [video_id]
    
    if filter_dict.get('class_name'):
        query_parts.append("AND class_name = ?")
        params.append(filter_dict['class_name'])
        
    if filter_dict.get('color'):
        query_parts.append("AND color = ?")
        params.append(filter_dict['color'])
        
    if filter_dict.get('spatial'):
        query_parts.append("AND spatial_relation = ?")
        params.append(filter_dict['spatial'])
        
    if filter_dict.get('exclude'):
        for ex in filter_dict['exclude']:
            query_parts.append("""
                AND NOT EXISTS (
                    SELECT 1 FROM detections d2 
                    WHERE d2.video_id = detections.video_id 
                    AND ROUND(d2.timestamp_s) = ROUND(detections.timestamp_s) 
                    AND d2.class_name = ?
                )
            """)
            params.append(ex)
            
    query_parts.append("GROUP BY ROUND(timestamp_s)")
    
    if filter_dict.get('count_op') and filter_dict.get('count_val') is not None:
        op = filter_dict['count_op']
        if op == '==': op = '='
        val = filter_dict['count_val']
        query_parts.append(f"HAVING COUNT(*) {op} ?")
        params.append(val)
        
    query_parts.append("ORDER BY window ASC")
    
    return "\n".join(query_parts), params

def search(filter_dict, video_id):
    """
    Returns list of dicts: [{'window': int, 'explanation': str}, ...]
    """
    query, params = build_search_query(filter_dict, video_id)
    
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        window = int(row['window'])
        det_count = row['det_count']
        max_conf = row['max_conf']
        
        parts = []
        if filter_dict.get('count_op'):
            parts.append(f"{det_count} {filter_dict.get('class_name', 'object')}s detected")
        else:
            cls_name = filter_dict.get('class_name') or 'object'
            parts.append(f"{cls_name} detected")
            
        if filter_dict.get('color'):
            parts.append(f"color {filter_dict['color']}")
        if filter_dict.get('spatial'):
            parts.append(filter_dict['spatial'])
        if filter_dict.get('exclude'):
            parts.append(f"no {', '.join(filter_dict['exclude'])}")
            
        explanation = f"Matched: {', '.join(parts)}, max confidence {max_conf:.2f}"
        
        bboxes_raw = row['bboxes']
        bboxes_list = []
        if bboxes_raw:
            for b in bboxes_raw.split(';'):
                parts_coords = b.split(',')
                if len(parts_coords) == 4:
                    bboxes_list.append([int(p) for p in parts_coords])
        
        results.append({
            'window': window,
            'explanation': explanation,
            'bboxes': bboxes_list
        })
        
    conn.close()
    return results
