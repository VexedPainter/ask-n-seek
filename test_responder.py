"""
Test suite for backend.nlp.responder — covers all 5 answer cases.

Uses realistic data shapes matching what search(), find_transition_events(),
and diagnose_no_match() actually return.
"""
import sys
sys.path.insert(0, '.')

from backend.nlp.responder import generate_answer

PASS_COUNT = 0
FAIL_COUNT = 0


def check(label, answer):
    global PASS_COUNT, FAIL_COUNT
    # Sanity: not empty, not a raw template placeholder
    ok = (
        isinstance(answer, str)
        and len(answer) > 10
        and '{' not in answer  # no leftover f-string placeholders
        and 'None' not in answer  # no leaking Nones
    )
    status = "PASS" if ok else "FAIL"
    if ok:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
    print(f"\n{'='*60}")
    print(f"[{status}] {label}")
    print(f"{'='*60}")
    print(f"  Answer: {answer}")
    return ok


# ─────────────────────────────────────────────────────────
# CASE 1: Zero results — unsupported vocabulary
# ─────────────────────────────────────────────────────────
filter_1 = {
    'class_name': None, 'color': None, 'exclude': [],
    'spatial': None, 'count_op': None, 'count_val': None,
    'event': None, 'unsupported_terms': ['helicopter']
}
diag_1 = {
    'type': 'unsupported_vocabulary',
    'terms': ['helicopter'],
    'message': "helicopter is outside our detection vocabulary"
}
answer_1 = generate_answer(filter_1, [], diag_1)
check("Zero results — unsupported vocabulary ('helicopter')", answer_1)

# ─────────────────────────────────────────────────────────
# CASE 2: Zero results — constraint failures
# ─────────────────────────────────────────────────────────
filter_2 = {
    'class_name': 'person', 'color': None, 'exclude': [],
    'spatial': 'touching:car', 'count_op': None, 'count_val': None,
    'event': None, 'unsupported_terms': [],
    'spatial_target_color': 'blue'
}
diag_2 = {
    'type': 'constraint_failures',
    'failures': ["Person is NOT touching a blue car in this video"],
    'hints': ["In this video, the person touches: red, white, gray cars. Try: 'person touching red car'"],
    'message': "constraint failure"
}
answer_2 = generate_answer(filter_2, [], diag_2)
check("Zero results — constraint failures (blue car not touched)", answer_2)

# ─────────────────────────────────────────────────────────
# CASE 3: Positive filter-search results (multiple)
# ─────────────────────────────────────────────────────────
filter_3 = {
    'class_name': 'person', 'color': None, 'exclude': [],
    'spatial': 'touching:car', 'count_op': None, 'count_val': None,
    'event': None, 'unsupported_terms': [],
    'spatial_target_color': 'red'
}
results_3 = [
    {'start': 2,  'end': 2,  'window': 2,  'explanation': 'Matched: person detected, touching:car (color: red), max confidence 0.89', 'bboxes': []},
    {'start': 20, 'end': 20, 'window': 20, 'explanation': 'Matched: person detected, touching:car (color: red), max confidence 0.85', 'bboxes': []},
    {'start': 28, 'end': 34, 'window': 28, 'explanation': 'Matched: person detected, touching:car (color: red), max confidence 0.91', 'bboxes': []},
]
answer_3 = generate_answer(filter_3, results_3, None)
check("Positive search — 3 results (person touching red car)", answer_3)

# ─────────────────────────────────────────────────────────
# CASE 3b: Single result
# ─────────────────────────────────────────────────────────
filter_3b = {
    'class_name': 'car', 'color': 'red', 'exclude': [],
    'spatial': None, 'count_op': None, 'count_val': None,
    'event': None, 'unsupported_terms': []
}
results_3b = [
    {'start': 4, 'end': 4, 'window': 4, 'explanation': 'Matched: car detected, color red, max confidence 0.93', 'bboxes': []},
]
answer_3b = generate_answer(filter_3b, results_3b, None)
check("Positive search — single result (red car)", answer_3b)

# ─────────────────────────────────────────────────────────
# CASE 3c: Many results
# ─────────────────────────────────────────────────────────
filter_3c = {
    'class_name': 'person', 'color': None, 'exclude': [],
    'spatial': None, 'count_op': None, 'count_val': None,
    'event': None, 'unsupported_terms': []
}
results_3c = [
    {'start': i*2, 'end': i*2, 'window': i*2, 'explanation': f'Matched: person detected, max confidence 0.88', 'bboxes': []}
    for i in range(15)
]
answer_3c = generate_answer(filter_3c, results_3c, None)
check("Positive search — many results (15 person detections)", answer_3c)

# ─────────────────────────────────────────────────────────
# CASE 4: Disappear event with results
# ─────────────────────────────────────────────────────────
filter_4 = {
    'class_name': 'person', 'color': None, 'exclude': [],
    'spatial': None, 'count_op': None, 'count_val': None,
    'event': 'disappear', 'unsupported_terms': []
}
results_4 = [
    {'start': 12, 'end': 12, 'explanation': 'person last seen at 10s, no longer detected from 12s'},
]
answer_4 = generate_answer(filter_4, results_4, None, event_type='disappear')
check("Event — person disappears once at 0:12", answer_4)

# ─────────────────────────────────────────────────────────
# CASE 4b: Multiple disappear events
# ─────────────────────────────────────────────────────────
results_4b = [
    {'start': 12, 'end': 12, 'explanation': 'person last seen at 10s, no longer detected from 12s'},
    {'start': 38, 'end': 38, 'explanation': 'person last seen at 36s, no longer detected from 38s'},
]
answer_4b = generate_answer(filter_4, results_4b, None, event_type='disappear')
check("Event — person disappears twice", answer_4b)

# ─────────────────────────────────────────────────────────
# CASE 4c: Reappear event
# ─────────────────────────────────────────────────────────
filter_4c = {
    'class_name': 'person', 'color': None, 'exclude': [],
    'spatial': None, 'count_op': None, 'count_val': None,
    'event': 'reappear', 'unsupported_terms': []
}
results_4c = [
    {'start': 25, 'end': 25, 'explanation': 'person reappears at 25s (last seen at 10s before disappearing)'},
]
answer_4c = generate_answer(filter_4c, results_4c, None, event_type='reappear')
check("Event — person reappears once at 0:25", answer_4c)

# ─────────────────────────────────────────────────────────
# CASE 5: Event — class never detected (empty results)
# ─────────────────────────────────────────────────────────
filter_5 = {
    'class_name': 'car', 'color': None, 'exclude': [],
    'spatial': None, 'count_op': None, 'count_val': None,
    'event': 'disappear', 'unsupported_terms': []
}
diag_5 = {
    'type': 'no_event',
    'message': "No disappear events found for 'car' in this video."
}
answer_5 = generate_answer(filter_5, [], diag_5, event_type='disappear')
check("Event — car never detected / never disappeared", answer_5)

# ─────────────────────────────────────────────────────────
# CASE 5b: Reappear — never detected
# ─────────────────────────────────────────────────────────
filter_5b = {
    'class_name': 'dog', 'color': None, 'exclude': [],
    'spatial': None, 'count_op': None, 'count_val': None,
    'event': 'reappear', 'unsupported_terms': []
}
diag_5b = {
    'type': 'no_event',
    'message': "No reappear events found for 'dog' in this video."
}
answer_5b = generate_answer(filter_5b, [], diag_5b, event_type='reappear')
check("Event — dog reappear, never detected", answer_5b)


# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"TOTAL: {PASS_COUNT + FAIL_COUNT} tests — {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED")
print(f"{'='*60}")
