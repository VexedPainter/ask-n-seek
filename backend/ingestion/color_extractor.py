import cv2
import numpy as np
from sklearn.cluster import KMeans

# Fixed color palette in RGB
COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'yellow': (255, 255, 0),
    'gray': (128, 128, 128),
    'orange': (255, 165, 0)
}

def closest_color(rgb_val):
    min_dist = float('inf')
    best_color = None
    for name, color in COLORS.items():
        dist = sum((a - b) ** 2 for a, b in zip(rgb_val, color))
        if dist < min_dist:
            min_dist = dist
            best_color = name
    return best_color

def extract_dominant_color(frame, bbox):
    """
    frame: numpy array (BGR from OpenCV)
    bbox: [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = bbox
    
    # Ensure bounds
    h, w = frame.shape[:2]
    x1, x2 = max(0, int(x1)), min(w, int(x2))
    y1, y2 = max(0, int(y1)), min(h, int(y2))
    
    if x2 <= x1 or y2 <= y1:
        return None
        
    cropped = frame[y1:y2, x1:x2]
    
    # Center crop (take middle 50%)
    ch, cw = cropped.shape[:2]
    cx1, cx2 = int(cw * 0.25), int(cw * 0.75)
    cy1, cy2 = int(ch * 0.25), int(ch * 0.75)
    
    if cx2 > cx1 and cy2 > cy1:
        cropped = cropped[cy1:cy2, cx1:cx2]
        
    if cropped.size == 0:
        return None
        
    # Resize to 32x32 to speed up k-means
    cropped = cv2.resize(cropped, (32, 32))
    
    # Convert to RGB
    cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    
    # Reshape for k-means
    pixels = cropped_rgb.reshape(-1, 3)
    
    # K-means to find dominant color
    try:
        kmeans = KMeans(n_clusters=2, n_init=1, random_state=42)
        kmeans.fit(pixels)
        labels = kmeans.labels_
        counts = np.bincount(labels)
        dominant_cluster_idx = np.argmax(counts)
        dominant_rgb = kmeans.cluster_centers_[dominant_cluster_idx]
        return closest_color(dominant_rgb)
    except Exception:
        # Fallback if clustering fails
        return None
