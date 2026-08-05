import os
import uuid
import threading
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Imports for our logic.
# Because detector.py loads the model at module level, importing it here
# guarantees the YOLO model is loaded into memory exactly once at startup.
from backend.query.parser import parse_query
from backend.search.search import search
from backend.search.no_match import diagnose_no_match
from backend.search.summary import get_top_objects
from backend.search.events import find_transition_events
from backend.ingestion.pipeline import run_pipeline

app = FastAPI(title="Ask-N-Seek API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_state = {}
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    text: str
    video_id: str

def ingest_worker(job_id: str, file_path: str):
    try:
        job_state[job_id] = {"status": "RUNNING", "progress_pct": 10, "current_phase": "Extracting frames"}
        # run_pipeline will take ~15-25s. We aren't doing fine-grained progress callbacks yet.
        run_pipeline(file_path)
        job_state[job_id] = {"status": "COMPLETED", "progress_pct": 100, "current_phase": "Done"}
    except Exception as e:
        job_state[job_id] = {"status": "FAILED", "progress_pct": 0, "current_phase": str(e)}

@app.post("/ingest")
async def ingest_video(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    file_path = os.path.join(DATA_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    job_state[job_id] = {"status": "QUEUED", "progress_pct": 0, "current_phase": "Queued"}
    
    # Run in background thread, non-blocking
    thread = threading.Thread(target=ingest_worker, args=(job_id, file_path))
    thread.start()
    
    return {"job_id": job_id}

@app.get("/ingest/status/{job_id}")
def get_ingest_status(job_id: str):
    if job_id not in job_state:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_state[job_id]

@app.post("/query")
def run_query(req: QueryRequest):
    filter_dict = parse_query(req.text)
    
    # Catch completely unsupported queries so they don't return the entire database
    if filter_dict.get('unsupported_terms') and not filter_dict.get('class_name') and not filter_dict.get('color'):
        return {
            "results": [],
            "no_match_diagnosis": {
                "type": "unsupported_vocabulary",
                "message": f"Sorry, I don't know what '{filter_dict['unsupported_terms'][0]}' looks like. I only recognize basic objects like person, car, dog, etc."
            }
        }
    
    # --- Event query path (disappear / reappear) ---
    if filter_dict.get('event'):
        event_type = filter_dict['event']
        class_name = filter_dict.get('class_name') or 'person'  # default to person
        
        events = find_transition_events(req.video_id, class_name, event_type)
        
        no_match_diagnosis = None
        if not events:
            no_match_diagnosis = {
                "type": "no_event",
                "message": f"No {event_type} events found for '{class_name}' in this video. "
                           f"Either '{class_name}' was visible the entire time, or it was never detected at all."
            }
        
        return {
            "results": events,
            "event_type": event_type,
            "no_match_diagnosis": no_match_diagnosis
        }
    
    # --- Standard filter-based search path ---
    results = search(filter_dict, req.video_id)
    
    no_match_diagnosis = None
    if len(results) == 0:
        no_match_diagnosis = diagnose_no_match(filter_dict, req.video_id)
        
    return {
        "results": results,
        "no_match_diagnosis": no_match_diagnosis
    }

@app.get("/video/{video_id}/top-objects")
def top_objects(video_id: str):
    objects = get_top_objects(video_id)
    return {"objects": objects}

@app.get("/video/{filename}")
def get_video(filename: str):
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        if filename == "test_video_60s.mp4" and os.path.exists(filename):
            return FileResponse(filename)
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(file_path)

from fastapi.staticfiles import StaticFiles

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

app.mount("/", StaticFiles(directory="frontend"), name="frontend")
