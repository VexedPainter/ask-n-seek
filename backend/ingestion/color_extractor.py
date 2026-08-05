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
    c = np.uint8([[[rgb_val[0], rgb_val[1], rgb_val[2]]]])
    hsv = cv2.cvtColor(c, cv2.COLOR_RGB2HSV)[0][0]
    h, s, v = hsv
    
    # Grayscale check
    if s < 60:
        if v < 45:
            return 'black'
        elif v > 150:
            # Distinguish white from silver/gray based on extremely low saturation and high value
            if s < 30 and v > 180:
                return 'white'
            elif v > 200:
                return 'silver'
            else:
                return 'gray'
        else:
            return 'gray'
            
    # Brown is essentially dark orange
    if 10 <= h < 25 and v < 120:
        return 'brown'
        
    # Hue ranges
    if h < 8 or h > 170:
        # Check if it's pink (high value, somewhat lower saturation in red hue)
        if s < 150 and v > 150 and (h < 8 or h > 170):
            return 'pink'
        return 'red'
    elif 8 <= h < 25:
        return 'orange'
    elif 25 <= h < 35:
        return 'yellow'
    elif 35 <= h < 85:
        return 'green'
    elif 85 <= h < 100:
        return 'cyan'
    elif 100 <= h < 130:
        return 'blue'
    elif 130 <= h <= 170:
        if v > 150 and s < 150:
            return 'pink'
        return 'purple'
    
    return 'gray'

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
        
        # Sort clusters by pixel count
        idx_sorted = np.argsort(counts)[::-1]
        
        best_color = 'gray'
        for idx in idx_sorted:
            rgb = kmeans.cluster_centers_[idx]
            color_name = closest_color(rgb)
            # If the largest cluster is a real color (not black/white/gray), return it immediately!
            if color_name not in ['black', 'white', 'gray']:
                return color_name
            # Otherwise, keep the first (largest) fallback color, but check the second cluster just in case!
            if idx == idx_sorted[0]:
                best_color = color_name
                
        return best_color
    except Exception:
        return None
