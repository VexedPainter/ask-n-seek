import sys
sys.path.insert(0, '.')
from backend.query.parser import parse_query

queries = [
    'blue car',
    'blue color car',
    'person touching blue car',
    'person touching blue color car',
    'blue',
    'blue color',
]

for q in queries:
    r = parse_query(q)
    print(f"{q:40s} -> class={str(r['class_name']):10s} color={str(r['color']):6s} spatial={str(r.get('spatial')):20s} target_color={r.get('spatial_target_color')}")
