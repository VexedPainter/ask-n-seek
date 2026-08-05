import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.db.schema import get_connection

def diagnose_no_match(filter_dict, video_id):
    """
    Determines the reason a search returned 0 results.
    First checks vocabulary constraints, then individual database constraints.
    """
    # 1. Check unsupported terms
    unsupported = filter_dict.get('unsupported_terms', [])
    if unsupported:
        terms_str = ", ".join(unsupported)
        return {
            "type": "unsupported_vocabulary",
            "terms": unsupported,
            "message": f"{terms_str} is outside our detection vocabulary (COCO-80 object classes) — try a different query"
        }
        
    # 2. Check individual constraints against the database
    diagnostics = []
    conn = get_connection()
    cursor = conn.cursor()
    
    def count_matches(q, p):
        cursor.execute(q, p)
        return cursor.fetchone()[0]
        
    if filter_dict.get('class_name'):
        c = count_matches("SELECT COUNT(*) FROM detections WHERE video_id = ? AND class_name = ?", (video_id, filter_dict['class_name']))
        if c == 0:
            diagnostics.append(f"0 detections of class '{filter_dict['class_name']}'")
            
    if filter_dict.get('color'):
        c = count_matches("SELECT COUNT(*) FROM detections WHERE video_id = ? AND color = ?", (video_id, filter_dict['color']))
        if c == 0:
            diagnostics.append(f"0 detections with color '{filter_dict['color']}'")
            
    if filter_dict.get('spatial'):
        c = count_matches("SELECT COUNT(*) FROM detections WHERE video_id = ? AND spatial_relation = ?", (video_id, filter_dict['spatial']))
        if c == 0:
            diagnostics.append(f"0 detections with spatial relation '{filter_dict['spatial']}'")
            
    if filter_dict.get('count_op') and filter_dict.get('count_val') is not None:
        op = filter_dict['count_op']
        if op == '==': op = '='
        val = filter_dict['count_val']
        q = f"SELECT COUNT(*) FROM (SELECT COUNT(*) as c FROM detections WHERE video_id = ? GROUP BY ROUND(timestamp_s) HAVING c {op} ?)"
        c = count_matches(q, (video_id, val))
        if c == 0:
            diagnostics.append(f"0 frames satisfy the condition of {filter_dict['count_op']} {val} objects")
            
    conn.close()
    
    if not diagnostics:
        msg = "All individual constraints exist in the video, but their combination produced 0 matches."
    else:
        msg = "Constraint failures: " + "; ".join(diagnostics)
        
    return {
        "type": "constraint_failures",
        "failures": diagnostics,
        "message": msg
    }
