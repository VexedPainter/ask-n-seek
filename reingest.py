"""Re-ingest all videos in data/ with the updated spatial pipeline."""
import sys, os, glob
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.ingestion.pipeline import run_pipeline

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

videos = glob.glob(os.path.join(DATA_DIR, "*.mp4"))
print(f"Found {len(videos)} videos to re-ingest")

for i, v in enumerate(videos, 1):
    name = os.path.basename(v)
    print(f"\n[{i}/{len(videos)}] Ingesting: {name}")
    try:
        run_pipeline(v)
        print(f"  Done")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nAll videos re-ingested!")
