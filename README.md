<!-- Header Wave -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,50:333333,100:c4b8a5&height=200&section=header&text=Ask-N-Seek&fontSize=60&fontAlignY=35&desc=Type%20what%20happened.%20We'll%20show%20you%20exactly%20where.&descAlignY=55&descSize=20&fontColor=f5f3ef" width="100%"/>

<div align="center">

<!-- Animated Typing Text -->
<a href="https://github.com/VexedPainter/ask-n-seek">
  <img src="https://readme-typing-svg.demolab.com?font=Playfair+Display&weight=600&size=24&duration=3000&pause=1000&color=C4B8A5&center=true&vCenter=true&lines=Luxury+Computer+Vision;Zero-Build+Frontend;Natural+Language+Queries;CPU-Optimized+OpenVINO" alt="Typing SVG" />
</a>

<br>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenVINO-2C2255?style=for-the-badge&logo=intel&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Vanilla_JS-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
</p>

*An ultra-premium, CPU-optimized computer vision and natural language query engine.*

</div>

---

## ✧ The Vision

**Ask-N-Seek** bridges the gap between raw video footage and natural human inquiry. By leveraging an optimized, CPU-friendly OpenVINO YOLOv8n pipeline, it extracts object detections, color clusters, and spatial relations from any uploaded video. 

The intuitive, rule-based natural language parser translates plain English (*"red car left of the truck"*) into parameterized SQL constraints, instantly seeking your footage to the exact **6-second window of interest.**

<br>

## ✧ Core Engine

<table>
<tr>
<td valign="top" width="50%">

### 🧠 Inference & Processing
| Tech | Purpose |
|------|---------|
| **YOLOv8n** | Bounding box object detection |
| **OpenVINO** | CPU hardware acceleration |
| **Scikit-Learn** | K-Means color clustering |
| **OpenCV** | Frame extraction & manipulation |

</td>
<td valign="top" width="50%">

### ⚡ Architecture & UI
| Tech | Purpose |
|------|---------|
| **FastAPI** | Asynchronous HTTP endpoints |
| **SQLite3** | Relational constraint engine |
| **Python `threading`** | Non-blocking background jobs |
| **IntersectionObserver** | High-performance scroll reveals |

</td>
</tr>
</table>

---

## ✧ Premium Features

- 🎭 **Natural Language Parsing**: Translates human queries into strict database constraints (supports colors, classes, object exclusions, and spatial relations).
- 🎯 **Smart Bounding Box Highlighting**: Clicking a search result jumps to the exact timestamp, pauses the video, and automatically maps and draws a glowing bounding box exactly over the detected object.
- ⚙️ **CPU-Optimized Ingestion**: Runs YOLOv8 inference through OpenVINO, capable of running smoothly on low-power Intel CPUs. Automatically filters low-confidence (sub-50%) noise for pristine precision.
- 🩺 **Smart Vocabulary Diagnostics**: A transparent query system that actively catches non-COCO vocabulary (e.g., *"helmet"*, *"hat"*) and gracefully diagnoses constraint failures.
- 💎 **Zero-Build Frontend**: A premium, luxury editorial-themed HTML/CSS/JS frontend completely free of complex build steps or node modules. Features a bespoke, thread-yielding particle engine.
- 🚀 **Asynchronous Architecture**: Ingests videos in non-blocking background threads with millisecond-precision polling.

<br>

## ✧ Quick Start Guide

### 1. Requirements
- Python 3.10+
- Standard Intel x86 CPU (OpenVINO optimized)

### 2. Initialization
```bash
# Clone the repository
git clone https://github.com/VexedPainter/ask-n-seek.git
cd ask-n-seek

# Install dependencies
pip install fastapi uvicorn python-multipart requests scikit-learn ultralytics openvino
```

### 3. Ignite the Engine
```bash
# Start the FastAPI backend and integrated frontend
python -m uvicorn backend.main:app --port 8000
```
**Navigate to:** `http://localhost:8000`

---
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:c4b8a5,50:333333,100:000000&height=120&section=footer" width="100%"/>

**Ask-N-Seek v1.0**

*Engineered for minimal footprint, designed for maximum elegance.*

<p>
  <img src="https://img.shields.io/badge/Made_by-VexedPainter-c4b8a5?style=flat-square&logo=github&logoColor=black" />
</p>

</div>
