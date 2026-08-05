def compute_spatial_relations(detections):
    """
    Modifies detections in-place to add spatial_relation where applicable.
    Only considers top-4 objects by confidence.
    """
    for det in detections:
        det['spatial_relation'] = None
        
    if len(detections) < 2:
        return
        
    # Top 4 by confidence
    top_dets = sorted(detections, key=lambda d: d['confidence'], reverse=True)[:4]
    
    for i, det_i in enumerate(top_dets):
        cx_i = (det_i['bbox'][0] + det_i['bbox'][2]) / 2
        
        # Find highest confidence OTHER object to relate to
        target_j = 0 if i != 0 else 1
        if target_j < len(top_dets):
            det_j = top_dets[target_j]
            cx_j = (det_j['bbox'][0] + det_j['bbox'][2]) / 2
            
            if cx_i < cx_j:
                det_i['spatial_relation'] = f"left_of:{det_j['class_name']}"
            else:
                det_i['spatial_relation'] = f"right_of:{det_j['class_name']}"
