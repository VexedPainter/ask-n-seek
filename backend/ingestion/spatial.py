def get_intersection(bb1, bb2):
    x_left = max(bb1[0], bb2[0])
    y_top = max(bb1[1], bb2[1])
    x_right = min(bb1[2], bb2[2])
    y_bottom = min(bb1[3], bb2[3])
    if x_right > x_left and y_bottom > y_top:
        return True
    return False

def compute_spatial_relations(detections):
    """
    Modifies detections in-place to add spatial_relation and spatial_target_color.
    Evaluates intersection for 'touching', otherwise uses left/right.
    """
    for det in detections:
        det['spatial_relation'] = None
        det['spatial_target_color'] = None
        
    if len(detections) < 2:
        return
        
    # Top 4 by confidence to serve as targets
    top_dets = sorted(detections, key=lambda d: d['confidence'], reverse=True)[:4]
    
    for det_i in detections:
        # Check touching first
        for det_j in top_dets:
            if det_i is det_j: continue
            if get_intersection(det_i['bbox'], det_j['bbox']):
                det_i['spatial_relation'] = f"touching:{det_j['class_name']}"
                det_i['spatial_target_color'] = det_j.get('color')
                break
                
        # If no touching relation, assign left/right
        if not det_i['spatial_relation']:
            det_j = top_dets[0] if det_i is not top_dets[0] else (top_dets[1] if len(top_dets) > 1 else None)
            if det_j:
                cx_i = (det_i['bbox'][0] + det_i['bbox'][2]) / 2
                cx_j = (det_j['bbox'][0] + det_j['bbox'][2]) / 2
                if cx_i < cx_j:
                    det_i['spatial_relation'] = f"left_of:{det_j['class_name']}"
                else:
                    det_i['spatial_relation'] = f"right_of:{det_j['class_name']}"
                det_i['spatial_target_color'] = det_j.get('color')

