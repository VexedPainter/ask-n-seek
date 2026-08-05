import sqlite3

conn = sqlite3.connect('ask_n_seek.db')

print("=== ALL person spatial relations in Man + Car ===")
rows = conn.execute(
    "SELECT ROUND(timestamp_s) as ts, spatial_relation, spatial_target_color "
    "FROM detections WHERE video_id='Man + Car.mp4' AND class_name='person' "
    "AND spatial_relation IS NOT NULL ORDER BY ts"
).fetchall()
for r in rows:
    print(f"  ts={int(r[0])}s  {str(r[1]):20s}  target_color={r[2]}")

print("\n=== ALL car/truck detections with colors in Man + Car ===")
rows2 = conn.execute(
    "SELECT ROUND(timestamp_s) as ts, class_name, color, confidence "
    "FROM detections WHERE video_id='Man + Car.mp4' AND class_name IN ('car','truck') "
    "ORDER BY ts, confidence DESC"
).fetchall()
for r in rows2:
    print(f"  ts={int(r[0])}s  {r[1]:6s}  color={str(r[2]):8s}  conf={r[3]:.2f}")

print("\n=== Touching the Car: person spatial relations ===")
rows3 = conn.execute(
    "SELECT ROUND(timestamp_s) as ts, spatial_relation, spatial_target_color "
    "FROM detections WHERE video_id='Touching the Car.mp4' AND class_name='person' "
    "AND spatial_relation IS NOT NULL ORDER BY ts"
).fetchall()
for r in rows3:
    print(f"  ts={int(r[0])}s  {str(r[1]):20s}  target_color={r[2]}")

print("\n=== ALL unique colors across all videos ===")
rows4 = conn.execute(
    "SELECT DISTINCT color FROM detections WHERE color IS NOT NULL ORDER BY color"
).fetchall()
print("  Colors:", [r[0] for r in rows4])

conn.close()
