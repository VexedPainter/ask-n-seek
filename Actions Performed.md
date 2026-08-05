# Actions Performed: Advanced Engine Features

This document explains the technical architecture behind two of the most advanced features implemented in the Ask-N-Seek engine: **Empty Frame Negation** and **Simulated Action Recognition**.

---

## 1. The Negation Engine: Detecting "No Person"

### The Challenge: The "Ghost" Frame Problem
Standard object detection models like YOLOv8 are designed to detect *presence*, not *absence*. When the engine scans a video frame, it only records the objects it finds (e.g., cars, people, dogs). 

If a person walks behind a tree and disappears, the AI detects absolutely zero objects in that frame. To save memory, the AI normally skips recording empty frames into the database. Because these frames physically do not exist in the database, searching for a negative constraint like `"without a person"` or `"no person"` fails to return the frames where you are hiding, simply because the database has no record of that time period existing.

### The Solution: The Empty Frame Anchor
To solve this, we implemented a structural change to the database ingestion pipeline:
1. **The Anchor Row:** When the AI scans a frame and finds zero objects, instead of skipping the frame, it intentionally injects a dummy anchor row into the SQLite database with the label `__empty__`.
2. **Database Continuity:** This ensures that every single second of the video has at least one mathematical representation in the database, preserving the timeline's continuity.
3. **NLP Parsing:** When you type `"no person"` or `"zero people"`, the Natural Language Parser (NLP) intercepts these negative phrases and converts them into an SQL `NOT EXISTS` query. 
4. **Execution:** The SQL engine sweeps through the database, encounters the `__empty__` anchor frames, verifies that `person` does *not* exist in that frame, and perfectly returns the exact timestamps where you vanished.

---

## 2. Simulated Action Recognition: Touching, Grabbing, and Pulling

### The Challenge: Static Nouns vs. Dynamic Verbs
Object detection models (like YOLOv8) are static classifiers. They only understand nouns (e.g., drawing a box around a `person` or a `car`). They have absolutely no concept of verbs, poses, or actions like "grabbing," "touching," or "pulling." Normally, this requires a completely separate, resource-heavy neural network (like a Pose Estimation model) to detect the skeletal structure of a hand grabbing a door handle.

### The Solution: 2D Bounding Box Intersection Logic
To keep the engine lightweight and fast for the hackathon, we built an **Action Simulation Engine** directly into the spatial logic, bypassing the need for a heavy pose model.

1. **Intersection Math:** During the ingestion phase, the engine calculates the coordinates of every bounding box. We introduced a mathematical intersection function that evaluates if the 2D bounding box of a person physically overlaps with the bounding box of a car. 
2. **Spatial Tagging:** When you walk up to a car to grab the handle, your bounding box merges into the car's bounding box. The engine detects this aggressive overlap and secretly assigns a new spatial relation tag to you: `touching:car`.
3. **Verb Translation:** We upgraded the NLP parser to recognize specific human verbs like `"touching"`, `"grabbing"`, `"pulling"`, `"holding"`, and `"opening"`. 
4. **Execution:** When you search for `"person grabbing the car door"`, the NLP engine strips away the fluff, realizes that "grabbing" translates mathematically to a bounding box overlap, and queries the database for `class_name = 'person'` with `spatial_relation = 'touching:car'`. The system instantly returns the exact moment you reached for the door handle.
