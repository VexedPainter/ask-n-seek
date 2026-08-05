"""Generate a synthetic 60-second test video with moving shapes for benchmarking."""
import cv2
import numpy as np

output_path = "test_video_60s.mp4"
fps = 30
duration = 60  # seconds
width, height = 1280, 720
total_frames = fps * duration

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

print(f"Generating {duration}s test video at {fps} FPS ({total_frames} frames)...")

for i in range(total_frames):
    # Create a frame with gradient background
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Gradient background that shifts over time
    bg_shift = int(i * 0.1) % 180
    frame[:, :, 0] = np.linspace(bg_shift, bg_shift + 50, width, dtype=np.uint8)
    frame[:, :, 1] = np.linspace(20, 80, height, dtype=np.uint8).reshape(-1, 1)
    frame[:, :, 2] = 40
    
    # Moving rectangles (simulate objects)
    t = i / fps
    
    # Rectangle 1 - moves horizontally
    x1 = int((np.sin(t * 0.5) + 1) * 0.4 * width)
    cv2.rectangle(frame, (x1, 200), (x1 + 120, 350), (0, 255, 0), -1)
    
    # Rectangle 2 - moves diagonally
    x2 = int((np.cos(t * 0.3) + 1) * 0.35 * width)
    y2 = int((np.sin(t * 0.4) + 1) * 0.25 * height)
    cv2.rectangle(frame, (x2, y2), (x2 + 80, y2 + 80), (255, 0, 0), -1)
    
    # Circle - moves in circle
    cx = int(width / 2 + 200 * np.cos(t * 0.7))
    cy = int(height / 2 + 100 * np.sin(t * 0.7))
    cv2.circle(frame, (cx, cy), 40, (0, 0, 255), -1)
    
    # Small shapes
    for j in range(3):
        sx = int((np.sin(t * (0.2 + j * 0.15) + j) + 1) * 0.45 * width)
        sy = int((np.cos(t * (0.3 + j * 0.1) + j * 2) + 1) * 0.35 * height)
        cv2.rectangle(frame, (sx, sy), (sx + 40, sy + 40), (200, 200, 0), -1)
    
    out.write(frame)
    
    if (i + 1) % 300 == 0:
        print(f"  {i+1}/{total_frames} frames written...")

out.release()
print(f"Done! Saved to {output_path}")
