# Ask-N-Seek: Conversational UI & Multilingual Support Report

This report details the recent major architectural and frontend changes implemented to transform Ask-N-Seek from a standard search-bar application into a highly interactive, multilingual, conversational AI experience.

## 1. Natural Language Responder Engine (`backend/nlp/responder.py`)
We introduced a rule-based natural language generator to interpret raw database query results and turn them into conversational, human-readable answers. 
- **Deterministic & Lightweight:** It uses pre-defined templates based on the query state rather than making expensive external LLM API calls, ensuring zero latency and deterministic reliability.
- **Handles 5 distinct states:**
  1. **Positive Search Results:** Summarizes counts, timestamps, and confidence scores (e.g., *"Found the person touching the red car 3 times — first at 0:02, then at 0:20, and last at 0:28 (high confidence)."*).
  2. **Event Transitions (Disappear/Reappear):** Narrates the timeline explicitly (e.g., *"The person disappeared around 0:12 — it was visible before that and then dropped out of frame."*).
  3. **Constraint Failures:** Explicitly states *why* a query failed while offering hints based on actual video data (e.g., *"Person is NOT touching a blue car in this video. In this video, the person touches: red, white, gray cars."*).
  4. **Unsupported Vocabulary:** Gracefully informs the user when a word is outside the COCO-80 vocabulary (e.g., *"I can't detect 'helicopter'..."*).
  5. **Empty Event Results:** Clarifies if an object was present but never transitioned, or never detected at all.

## 2. Multilingual Support (`backend/nlp/language.py`)
To cater to a broader audience, the system now natively supports queries in **Hindi** and **Kannada** alongside English.
- **Offline Language Detection:** Uses the `langdetect` library to analyze the query locally, identifying the ISO code (en, hi, kn) without network calls. We also implemented a custom fix to properly route related Devanagari scripts (like Nepali/Marathi) to Hindi for better translation accuracy.
- **Graceful Translation:** Uses `deep-translator` (Google Translate API) to seamlessly translate non-English queries to English before they hit the parser, and translates the final answer back to the user's native language. 
- **Fault-Tolerant:** If the network goes down or the translation API times out, the system degrades gracefully, returning the original text and an English fallback response rather than crashing the application.

## 3. Unified Conversational Endpoint (`backend/main.py`)
We created a new POST `/chat` endpoint specifically for the conversational UI.
- **Additive Design:** The existing `/query` endpoint was left completely intact to ensure backward compatibility and a separation of concerns.
- **Orchestration:** The new endpoint handles the complete lifecycle of a conversational query:
  1. Detects the language of the incoming query.
  2. Translates to English (if necessary).
  3. Parses the query into a filter dictionary.
  4. Routes to either the Event or Search logic depending on the parsed intent.
  5. Feeds the raw results and any diagnostics into the NL Responder to generate the text reply.
  6. Translates the reply back to the user's language (if necessary).
  7. Returns both the text reply and the raw results (for UI rendering).

## 4. Conversational Chat UI (`frontend/`)
We overhauled the frontend to include a ChatGPT-style conversational panel that acts as a side-by-side alternative to the standard search box.
- **Non-Destructive Integration:** The chat panel was added *without* breaking or hiding the existing search layout, hero section, upload zone, or top-objects grid.
- **Bubble UI:** Implemented smooth, animated chat bubbles. User messages are right-aligned with a cyan tint, while AI responses are left-aligned inside glassmorphic containers with custom avatars (✧).
- **Interactive Inline Results:** If a query yields results, the AI bubble renders compact, clickable "timestamp chips" (e.g., `▶ 00:02`). Clicking these chips smoothly scrolls the user to the video player, automatically seeks to the exact timestamp, and initiates playback (reusing the new `seekToTimestamp` logic extracted for DRY principles).
- **Visual Polish:** Added a dynamic, bouncing typing indicator (`...`) that displays while the server is processing the request, and language-detection tags (e.g., `Detected: Hindi`) appended to AI bubbles.

## Efficiency & Performance
- **Zero LLM Overhead:** Because the parsing (`parser.py`) and response generation (`responder.py`) are entirely rule-based and deterministic, the backend requires very little CPU power and no GPU overhead for text processing.
- **Minimal Network Dependency:** The only external network dependency is the lightweight Google Translate API call. If this fails, the system continues to work locally in English.
- **Responsive Frontend:** The UI uses vanilla JavaScript with no heavy frameworks (like React or Vue), relying entirely on DOM manipulation. The existing CSS design tokens were heavily reused, keeping the stylesheet lean and the aesthetic perfectly consistent.
