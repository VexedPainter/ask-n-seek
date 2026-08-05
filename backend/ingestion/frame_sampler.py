import cv2
import logging

logger = logging.getLogger(__name__)

def resize_longest_side(frame, target_size=416):
    h, w = frame.shape[:2]
    if w >= h:
        new_w = target_size
        new_h = int(h * target_size / w)
    else:
        new_h = target_size
        new_w = int(w * target_size / h)
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

def sample_frames(video_path, max_frames=30, interval_sec=2.0):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    if duration > 60:
        print(f"WARNING: Video duration ({duration:.1f}s) exceeds 60s cap. Auto-trimming.")

    frames = []
    for i in range(max_frames):
        timestamp_sec = i * interval_sec
        if timestamp_sec > duration or timestamp_sec > 60:
            break
            
        frame_number = int(timestamp_sec * fps)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if not ret:
            print(f"WARNING: Could not read frame at {timestamp_sec}s")
            continue
            
        frame = resize_longest_side(frame, 416)
        frames.append((timestamp_sec, frame))

    cap.release()
    return frames
