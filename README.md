<div align="center">

# ✦ Ask-N-Seek ✦

**Type what happened. We'll show you exactly where — and prove it.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenVINO](https://img.shields.io/badge/OpenVINO-2C2255?style=for-the-badge&logo=intel)](https://docs.openvino.ai/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite)](https://sqlite.org/)
[![Vanilla JS](https://img.shields.io/badge/Vanilla_JS-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

*A luxury, zero-build, CPU-optimized computer vision and natural language query engine.*

</div>

---

## ✧ Overview

**Ask-N-Seek** bridges the gap between raw video footage and natural human inquiry. By leveraging an optimized, CPU-friendly OpenVINO YOLOv8n pipeline, it extracts object detections, color clusters, and spatial relations from any uploaded video. 

The intuitive, rule-based natural language parser translates plain English ("red car left of the truck") into parameterized SQL constraints, instantly seeking your footage to the exact 6-second window of interest.

<br>

## ✧ Key Features

- **Natural Language Parsing**: Translates human queries into strict database constraints (supports colors, classes, object exclusions, and spatial relations).
- **CPU-Optimized Ingestion**: Runs YOLOv8 inference through OpenVINO, capable of running smoothly on low-power Intel CPUs without requiring dedicated GPUs.
- **Smart Vocabulary Diagnostics**: A transparent query system that actively catches non-COCO vocabulary (e.g., "helmet", "hat") and gracefully diagnoses constraint failures instead of throwing opaque zero-match errors.
- **Zero-Build Frontend**: A premium, luxury editorial-themed HTML/CSS/JS frontend completely free of complex build steps or node modules. Features IntersectionObserver scroll animations and a bespoke, thread-yielding particle engine.
- **Asynchronous FastAPI Architecture**: Ingests videos in non-blocking background threads with millisecond-precision status polling.

<br>

## ✧ Architecture

The system is cleanly decoupled into two layers:

### The Engine (Backend)
- **FastAPI Core**: Orchestrates endpoints for upload, ingestion status, queries, and media serving.
- **Ingestion Pipeline**: Samples footage at 2-second intervals. Extracts bounding boxes (YOLOv8n), determines dominant colors via K-Means clustering, and infers spatial relationships for top-confidence objects.
- **Search Module**: Dynamically builds parameterized SQLite queries, groups matching windows, and provides natural-language diagnosis for query failures.

### The Interface (Frontend)
- **Aesthetic First**: Built around the `Playfair Display`, `Inter`, and `JetBrains Mono` font families.
- **Performance Aware**: The `<canvas>` particle background selectively pauses its `requestAnimationFrame` loop during CPU-intensive video ingestion.

<br>

## ✧ Getting Started

### 1. Requirements
- Python 3.10+
- A machine capable of running OpenVINO (Standard Intel x86 CPUs work perfectly).

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/ask-n-seek.git
cd ask-n-seek

# Install dependencies
pip install fastapi uvicorn python-multipart requests scikit-learn ultralytics openvino
```

### 3. Launch the Backend
```bash
# Start the FastAPI server (runs on port 8000)
python -m uvicorn backend.main:app --reload --port 8000
```

### 4. Launch the Frontend
```bash
# In a new terminal, serve the frontend folder (runs on port 3000)
cd frontend
python -m http.server 3000
```

*Open [http://localhost:3000](http://localhost:3000) in your browser to experience Ask-N-Seek.*

<br>

## ✧ System Constraints

- **Vocabulary**: The search engine currently recognizes the standard 80 COCO objects. 
- **Video Length**: Designed for short-form footage. Videos exceeding 60 seconds are automatically trimmed during ingestion.

---
<div align="center">
  <i>Engineered for minimal footprint, designed for maximum elegance.</i>
</div>
