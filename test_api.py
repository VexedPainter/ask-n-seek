import time
import requests
import json

BASE_URL = "http://localhost:8000"

print("1. Testing /health...")
r = requests.get(f"{BASE_URL}/health")
print("Response:", r.json())
assert r.json()["status"] == "ok"

print("\n2. Uploading test_video_60s.mp4 to /ingest...")
with open("test_video_60s.mp4", "rb") as f:
    files = {"file": ("test_api_video.mp4", f, "video/mp4")}
    r = requests.post(f"{BASE_URL}/ingest", files=files)

res = r.json()
print("Response:", res)
job_id = res["job_id"]

print(f"\n3. Polling status for job {job_id}...")
while True:
    r = requests.get(f"{BASE_URL}/ingest/status/{job_id}")
    status = r.json()
    print(f"  {status}")
    if status["status"] == "COMPLETED":
        print("Ingestion finished!")
        break
    elif status["status"] == "FAILED":
        print("Ingestion failed!")
        break
    time.sleep(2)

print("\n4. Testing /query with a positive match ('red frisbee')...")
query_payload = {
    "text": "red frisbee",
    "video_id": "test_api_video.mp4"
}
r = requests.post(f"{BASE_URL}/query", json=query_payload)
print(json.dumps(r.json(), indent=2))

print("\n5. Testing /query with a zero match ('blue gentleman wearing no hat')...")
query_payload_2 = {
    "text": "blue gentleman wearing no hat",
    "video_id": "test_api_video.mp4"
}
r2 = requests.post(f"{BASE_URL}/query", json=query_payload_2)
print(json.dumps(r2.json(), indent=2))
