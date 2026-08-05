import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.db.schema import get_connection

VEHICLE_CLASSES = {'car', 'truck', 'bus'}

def diagnose_no_match(filter_dict, video_id):
    """
    Determines the reason a search returned 0 results.
    Provides actionable hints showing what IS available in the video.
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
    hints = []
    conn = get_connection()
    cursor = conn.cursor()
    
    def count_matches(q, p):
        cursor.execute(q, p)
        return cursor.fetchone()[0]
    
    def fetch_list(q, p):
        cursor.execute(q, p)
        return [r[0] for r in cursor.fetchall()]
        
    if filter_dict.get('class_name'):
        cls = filter_dict['class_name']
        if cls in VEHICLE_CLASSES:
            placeholders = ', '.join(['?' for _ in VEHICLE_CLASSES])
            c = count_matches(
                f"SELECT COUNT(*) FROM detections WHERE video_id = ? AND class_name IN ({placeholders})",
                (video_id, *VEHICLE_CLASSES)
            )
        else:
            c = count_matches(
                "SELECT COUNT(*) FROM detections WHERE video_id = ? AND class_name = ?",
                (video_id, cls)
            )
        if c == 0:
            available = fetch_list(
                "SELECT DISTINCT class_name FROM detections WHERE video_id = ? AND class_name != '__empty__' ORDER BY class_name",
                (video_id,)
            )
            diagnostics.append(f"No '{cls}' detected in this video")
            if available:
                hints.append(f"Objects in this video: {', '.join(available)}")
            
    if filter_dict.get('color'):
        c = count_matches(
            "SELECT COUNT(*) FROM detections WHERE video_id = ? AND color = ?",
            (video_id, filter_dict['color'])
        )
        if c == 0:
            available = fetch_list(
                "SELECT DISTINCT color FROM detections WHERE video_id = ? AND color IS NOT NULL ORDER BY color",
                (video_id,)
            )
            diagnostics.append(f"No objects with color '{filter_dict['color']}'")
            if available:
                hints.append(f"Colors in this video: {', '.join(available)}")
            
    if filter_dict.get('spatial'):
        spatial = filter_dict['spatial']
        parts = spatial.split(':')
        relation_type = parts[0] if len(parts) == 2 else None
        target_cls = parts[1] if len(parts) == 2 else None
        
        # Check with vehicle equivalence
        if target_cls and target_cls in VEHICLE_CLASSES:
            placeholders = ', '.join(['?' for _ in VEHICLE_CLASSES])
            spatial_variants = [f"{relation_type}:{v}" for v in VEHICLE_CLASSES]
            c = count_matches(
                f"SELECT COUNT(*) FROM detections WHERE video_id = ? AND spatial_relation IN ({placeholders})",
                (video_id, *spatial_variants)
            )
        else:
            c = count_matches(
                "SELECT COUNT(*) FROM detections WHERE video_id = ? AND spatial_relation = ?",
                (video_id, spatial)
            )
        if c == 0:
            diagnostics.append(f"No '{spatial}' relations found")
    
    # Check spatial_target_color specifically — this is often the real culprit
    if filter_dict.get('spatial_target_color') and filter_dict.get('spatial'):
        target_color = filter_dict['spatial_target_color']
        spatial = filter_dict['spatial']
        parts = spatial.split(':')
        relation_type = parts[0] if len(parts) == 2 else None
        
        # Find what target colors ARE available for this relation
        if relation_type:
            available_colors = fetch_list(
                "SELECT DISTINCT spatial_target_color FROM detections "
                "WHERE video_id = ? AND spatial_relation LIKE ? AND spatial_target_color IS NOT NULL "
                "ORDER BY spatial_target_color",
                (video_id, f"{relation_type}:%")
            )
            
            if target_color not in available_colors:
                if available_colors:
                    diagnostics.append(
                        f"Person is NOT touching a {target_color} car in this video"
                    )
                    hints.append(
                        f"In this video, the person touches: {', '.join(available_colors)} cars. "
                        f"Try: 'person touching {available_colors[0]} car'"
                    )
                else:
                    diagnostics.append(f"No touching relations with any colored target found")
            
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
        msg = "; ".join(diagnostics)
        if hints:
            msg += " | Hint: " + " | ".join(hints)
        
    return {
        "type": "constraint_failures",
        "failures": diagnostics,
        "hints": hints,
        "message": msg
    }
