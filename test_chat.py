"""Test /chat endpoint with English, Hindi, and Kannada queries."""
import sys
import io
import json
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "http://localhost:8000"
VIDEO = "Man + Car.mp4"

queries = [
    ("English", "person touching red car"),
    ("Hindi",   "लाल कार को छू रहा व्यक्ति"),
    ("Kannada", "ಕೆಂಪು ಕಾರನ್ನು ಮುಟ್ಟುತ್ತಿರುವ ವ್ಯಕ್ತಿ"),
]

for label, text in queries:
    print(f"\n{'='*60}")
    print(f"TEST: {label} — \"{text}\"")
    print(f"{'='*60}")

    resp = requests.post(f"{BASE}/chat", json={"text": text, "video_id": VIDEO})

    if resp.status_code != 200:
        print(f"  ERROR: HTTP {resp.status_code} — {resp.text}")
        continue

    data = resp.json()
    print(f"  language_detected: {data.get('language_detected')}")
    print(f"  event_type:        {data.get('event_type')}")
    print(f"  reply:             {data.get('reply')}")
    print(f"  results count:     {len(data.get('results', []))}")

    if data.get('results'):
        first = data['results'][0]
        print(f"  first result:      start={first.get('start')}s, explanation={first.get('explanation')}")

print(f"\n{'='*60}")
print("ALL TESTS COMPLETE")
print(f"{'='*60}")
