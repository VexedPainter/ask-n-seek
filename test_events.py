"""
End-to-end test: verifies event detection against the raw detections table.

Approach:
 1. Pick the first video_id that exists in the database.
 2. For a tracked class (person), dump the raw presence/absence timeline
    from the detections table.
 3. Manually compute expected disappear transitions from that timeline.
 4. Call find_transition_events() and compare against expectations.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.db.schema import get_connection
from backend.search.events import find_transition_events
import sqlite3


def main():
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    # 1. Find a video_id that has data
    row = conn.execute("SELECT DISTINCT video_id FROM detections LIMIT 1").fetchone()
    if not row:
        print("No data in detections table. Ingest a video first.")
        return
    video_id = row['video_id']
    print(f"Testing with video_id = '{video_id}'")

    # 2. Get full timeline
    all_ts = [
        int(r['ts']) for r in conn.execute(
            "SELECT DISTINCT ROUND(timestamp_s) AS ts FROM detections "
            "WHERE video_id = ? ORDER BY ts ASC", (video_id,)
        ).fetchall()
    ]
    print(f"Total frames in timeline: {len(all_ts)}  (range {all_ts[0]}s - {all_ts[-1]}s)")

    # 3. Check presence of 'person' at each timestamp
    person_ts = {
        int(r['ts']) for r in conn.execute(
            "SELECT DISTINCT ROUND(timestamp_s) AS ts FROM detections "
            "WHERE video_id = ? AND class_name = 'person'", (video_id,)
        ).fetchall()
    }
    conn.close()
    print(f"Timestamps where 'person' is present: {sorted(person_ts)}")
    print(f"Timestamps where 'person' is absent:  {sorted(set(all_ts) - person_ts)}")

    # 4. Manually compute expected disappear events
    expected_disappear = []
    for i in range(len(all_ts) - 1):
        t_curr, t_next = all_ts[i], all_ts[i + 1]
        if t_curr in person_ts and t_next not in person_ts:
            expected_disappear.append(t_next)

    expected_reappear = []
    for i in range(len(all_ts) - 1):
        t_curr, t_next = all_ts[i], all_ts[i + 1]
        if t_curr not in person_ts and t_next in person_ts:
            expected_reappear.append(t_next)

    print(f"\nExpected DISAPPEAR transition timestamps: {expected_disappear}")
    print(f"Expected REAPPEAR  transition timestamps: {expected_reappear}")

    # 5. Call the function under test
    disappear_results = find_transition_events(video_id, 'person', 'disappear')
    reappear_results  = find_transition_events(video_id, 'person', 'reappear')

    disappear_ts = [r['start'] for r in disappear_results]
    reappear_ts  = [r['start'] for r in reappear_results]

    print(f"\nActual DISAPPEAR results: {disappear_ts}")
    for r in disappear_results:
        print(f"  {r}")
    print(f"Actual REAPPEAR  results: {reappear_ts}")
    for r in reappear_results:
        print(f"  {r}")

    # 6. Assertions
    assert disappear_ts == expected_disappear, \
        f"DISAPPEAR mismatch: expected {expected_disappear}, got {disappear_ts}"
    assert reappear_ts == expected_reappear, \
        f"REAPPEAR mismatch: expected {expected_reappear}, got {reappear_ts}"

    print("\n" + "=" * 60)
    print("ALL EVENT DETECTION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
