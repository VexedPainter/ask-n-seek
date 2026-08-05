import sqlite3
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.db.schema import get_connection


def find_transition_events(video_id, class_name, event_type):
    """
    Finds disappearance or reappearance transition events for a given class
    in a video by walking the ordered frame timeline and detecting
    presence-to-absence (or reverse) flips.

    Args:
        video_id (str): The video identifier.
        class_name (str): The COCO class to track (e.g. "person", "car").
        event_type (str): "disappear" or "reappear".

    Returns:
        list of dicts, each with keys: start, end, explanation.
        Returns [] if class_name was never detected in this video at all.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Get all distinct rounded timestamps for this video, ordered ascending.
    #    This gives us the full frame timeline (including __empty__ anchors).
    cursor.execute(
        "SELECT DISTINCT ROUND(timestamp_s) AS ts FROM detections "
        "WHERE video_id = ? ORDER BY ts ASC",
        (video_id,)
    )
    all_timestamps = [int(row['ts']) for row in cursor.fetchall()]

    if not all_timestamps:
        conn.close()
        return []

    # 2. Get the set of timestamps where this specific class IS present.
    cursor.execute(
        "SELECT DISTINCT ROUND(timestamp_s) AS ts FROM detections "
        "WHERE video_id = ? AND class_name = ?",
        (video_id, class_name)
    )
    present_timestamps = {int(row['ts']) for row in cursor.fetchall()}

    conn.close()

    # If the class was never detected anywhere, return empty — let the
    # caller handle "never appeared" as a distinct case.
    if not present_timestamps:
        return []

    # 3. Walk the timeline and detect transitions.
    results = []

    for i in range(len(all_timestamps) - 1):
        t_curr = all_timestamps[i]
        t_next = all_timestamps[i + 1]

        curr_present = t_curr in present_timestamps
        next_present = t_next in present_timestamps

        if event_type == "disappear" and curr_present and not next_present:
            # Present at t_curr, absent at t_next → disappearance confirmed at t_next
            results.append({
                'start': t_next,
                'end': t_next,
                'explanation': (
                    f"{class_name} last seen at {t_curr}s, "
                    f"no longer detected from {t_next}s"
                ),
            })

        elif event_type == "reappear" and not curr_present and next_present:
            # Absent at t_curr, present at t_next → reappearance at t_next
            results.append({
                'start': t_next,
                'end': t_next,
                'explanation': (
                    f"{class_name} reappears at {t_next}s "
                    f"(last seen at {t_curr}s before disappearing)"
                ),
            })

    return results
