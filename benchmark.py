"""
CPU-only YOLOv8n + OpenVINO object detection benchmark.
Loads YOLOv8n, exports to OpenVINO format, runs inference on 30 frames
extracted at fixed 2-second intervals from a video, and reports timing.
"""

import sys
import time
import os
import cv2
from pathlib import Path
from ultralytics import YOLO


def resize_longest_side(frame, target_size=416):
    """Resize frame so the longest side equals target_size, preserving aspect ratio."""
    h, w = frame.shape[:2]
    if w >= h:
        new_w = target_size
        new_h = int(h * target_size / w)
    else:
        new_h = target_size
        new_w = int(w * target_size / h)
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)


def extract_frames(video_path, num_frames=30, interval_sec=2.0):
    """Extract exactly num_frames at fixed interval_sec intervals."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames_in_video = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames_in_video / fps if fps > 0 else 0

    print(f"Video: {video_path}")
    print(f"  FPS: {fps:.1f}, Total frames: {total_frames_in_video}, Duration: {duration:.1f}s")
    print(f"  Extracting {num_frames} frames at {interval_sec}s intervals...")

    frames = []
    for i in range(num_frames):
        timestamp_sec = i * interval_sec
        frame_number = int(timestamp_sec * fps)

        # If we exceed video length, wrap around
        if frame_number >= total_frames_in_video:
            frame_number = frame_number % total_frames_in_video

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if not ret:
            # Fallback: restart from beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                print(f"  WARNING: Could not read frame {i}, skipping")
                continue

        frame = resize_longest_side(frame, 416)
        frames.append(frame)

    cap.release()
    print(f"  Extracted {len(frames)} frames (resized to 416px longest side)")
    return frames


def load_openvino_model():
    """Load YOLOv8n, export to OpenVINO if needed, and return the OV model."""
    pt_model_path = "yolov8n.pt"
    ov_model_dir = Path("yolov8n_openvino_model")

    # Check if OpenVINO model already exists
    ov_xml = ov_model_dir / "yolov8n.xml"
    if ov_xml.exists():
        print(f"OpenVINO model already exists at: {ov_model_dir}")
    else:
        print("Exporting YOLOv8n to OpenVINO format...")
        base_model = YOLO(pt_model_path)
        export_path = base_model.export(format="openvino")
        print(f"Exported to: {export_path}")

    # Load the OpenVINO model explicitly for inference
    print("Loading OpenVINO model for inference...")
    ov_model = YOLO(str(ov_model_dir))
    print("OpenVINO model loaded successfully.")
    return ov_model


def run_benchmark(model, frames):
    """Run detection on each frame and record per-frame inference time."""
    print(f"\nRunning inference on {len(frames)} frames...")
    print("-" * 50)

    per_frame_times = []

    for i, frame in enumerate(frames):
        start = time.perf_counter()
        results = model(frame, verbose=False)
        elapsed = time.perf_counter() - start
        elapsed_ms = elapsed * 1000

        per_frame_times.append(elapsed_ms)

        num_detections = len(results[0].boxes) if results else 0
        print(f"  Frame {i+1:2d}/{len(frames)}: {elapsed_ms:7.1f} ms  ({num_detections} detections)")

    return per_frame_times


def print_results(per_frame_times):
    """Print summary statistics and verdict."""
    total_frames = len(per_frame_times)
    total_time_ms = sum(per_frame_times)
    total_time_s = total_time_ms / 1000
    avg_ms = total_time_ms / total_frames if total_frames > 0 else 0

    print("\n" + "=" * 50)
    print("BENCHMARK RESULTS")
    print("=" * 50)
    print(f"  Total frames processed : {total_frames}")
    print(f"  Average ms/frame       : {avg_ms:.1f} ms")
    print(f"  Total detection time   : {total_time_s:.2f} s ({total_time_ms:.0f} ms)")
    print()

    if total_time_s < 15:
        print("  VERDICT: ✅ GOOD (under 15s total)")
    elif total_time_s <= 30:
        print("  VERDICT: ⚠️  ACCEPTABLE (15-30s)")
    else:
        print("  VERDICT: ❌ TOO SLOW (over 30s) — reduce frame count to 15-20 or resolution to 320px")

    print("=" * 50)


def main():
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py <video_file_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    if not os.path.isfile(video_path):
        print(f"ERROR: File not found: {video_path}")
        sys.exit(1)

    print("=" * 50)
    print("YOLOv8n + OpenVINO CPU Benchmark")
    print("=" * 50)

    # Step 1: Load model
    model = load_openvino_model()

    # Step 2: Extract frames
    frames = extract_frames(video_path)

    # Step 3: Run benchmark
    per_frame_times = run_benchmark(model, frames)

    # Step 4: Print results
    print_results(per_frame_times)


if __name__ == "__main__":
    main()
