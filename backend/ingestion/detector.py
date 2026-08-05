from pathlib import Path
from ultralytics import YOLO

# Load OpenVINO model once at module level (from benchmark.py)
ov_model_dir = Path(__file__).parent.parent.parent / "yolov8n_openvino_model"
if not ov_model_dir.exists():
    raise RuntimeError(f"OpenVINO model not found at {ov_model_dir}. Please run benchmark.py first.")

model = YOLO(str(ov_model_dir), task='detect')

def detect(frame):
    """
    Returns list of dicts: {class_name, confidence, bbox: [x1, y1, x2, y2]}
    """
    results = model(frame, verbose=False, conf=0.50)
    detections = []
    
    if not results:
        return detections
        
    result = results[0]
    names = result.names
    
    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        
        detections.append({
            'class_name': names[cls_id],
            'confidence': conf,
            'bbox': [int(x1), int(y1), int(x2), int(y2)]
        })
        
    return detections
