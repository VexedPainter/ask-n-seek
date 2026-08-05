import sys
sys.path.insert(0, '.')
from backend.query.parser import parse_query

queries = [
    'person touching red car',
    'person touching blue car',
    'person touching white car',
    'person touching black car',
    'person touching gray car',
]

for q in queries:
    r = parse_query(q)
    print(f"{q:35s} -> spatial={str(r.get('spatial')):20s} target_color={r.get('spatial_target_color')}")

print("\n=== DB check: what target colors exist ===")
import sqlite3
conn = sqlite3.connect('ask_n_seek.db')
rows = conn.execute("SELECT DISTINCT spatial_target_color FROM detections WHERE spatial_relation LIKE 'touching:%'").fetchall()
print("Available spatial_target_colors:", [r[0] for r in rows])

print("\n=== Per-color count for person touching car ===")
for color in ['red', 'blue', 'white', 'black', 'gray']:
    count = conn.execute(
        "SELECT COUNT(*) FROM detections WHERE class_name='person' AND spatial_relation='touching:car' AND spatial_target_color=?",
        (color,)
    ).fetchone()[0]
    print(f"  {color:8s}: {count} rows")
conn.close()
