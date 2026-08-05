import sys
import time
import os

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.db.schema import create_tables, insert_detections, get_connection
from backend.ingestion.frame_sampler import sample_frames
from backend.ingestion.detector import detect
from backend.ingestion.color_extractor import extract_dominant_color
from backend.ingestion.spatial import compute_spatial_relations

def run_pipeline(video_path):
    start_time = time.perf_counter()
    video_id = os.path.basename(video_path)
    
    print("1. Creating database tables...")
    create_tables()
    
    print(f"2. Extracting frames from {video_path}...")
    frames = sample_frames(video_path)
    print(f"   Done. Extracted {len(frames)} frames.")
    
    all_db_rows = []
    
    print("3. Running detection, color extraction, and spatial analysis...")
    for idx, (timestamp_s, frame) in enumerate(frames):
        # Detection
        detections = detect(frame)
        
        # Color Extraction
        for det in detections:
            det['color'] = extract_dominant_color(frame, det['bbox'])
            
        # Spatial Relations
        compute_spatial_relations(detections)
        
        # Format for DB
        if not detections:
            all_db_rows.append({
                'video_id': video_id,
                'timestamp_s': timestamp_s,
                'class_name': '__empty__',
                'confidence': 0.0,
                'color': None,
                'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0,
                'spatial_relation': None,
                'spatial_target_color': None
            })
        else:
            for det in detections:
                all_db_rows.append({
                    'video_id': video_id,
                    'timestamp_s': timestamp_s,
                    'class_name': det['class_name'],
                    'confidence': float(det['confidence']),
                    'color': det['color'],
                    'x1': det['bbox'][0],
                    'y1': det['bbox'][1],
                    'x2': det['bbox'][2],
                    'y2': det['bbox'][3],
                    'spatial_relation': det['spatial_relation'],
                    'spatial_target_color': det.get('spatial_target_color')
                })
            
        if (idx + 1) % 5 == 0:
            print(f"   Processed {idx + 1}/{len(frames)} frames...")
            
    print("4. Writing to SQLite...")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM detections WHERE video_id = ?", (video_id,))
    conn.commit()
    conn.close()
    
    insert_detections(all_db_rows)
    print(f"   Done. Inserted {len(all_db_rows)} rows.")
    
    total_time = time.perf_counter() - start_time
    print(f"\nPipeline finished in {total_time:.2f} seconds wall-clock time.")
    
    # Print 5 sample rows
    print("\nSample rows from SQLite (up to 5):")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detections LIMIT 5")
    rows = cursor.fetchall()
    
    # Get column names
    col_names = [description[0] for description in cursor.description]
    
    # Print header
    header = " | ".join(f"{name:12}" for name in col_names)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows:
        row_str = " | ".join(f"{str(val):12}" for val in row)
        print(row_str)
        
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <video_path>")
        sys.exit(1)
    run_pipeline(sys.argv[1])
