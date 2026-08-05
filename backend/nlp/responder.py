"""
Natural-language answer generator.

Turns raw search/event results + diagnosis dicts into a single
conversational answer string. Rule-based templates only — no LLM calls.
"""


def _fmt_time(seconds):
    """Format seconds as M:SS."""
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def _confidence_label(explanation):
    """Extract confidence from an explanation string and return a plain label."""
    try:
        # Explanation format: "... max confidence 0.87"
        conf = float(explanation.rsplit("confidence ", 1)[1])
    except (IndexError, ValueError):
        return "moderate"
    if conf >= 0.85:
        return "high"
    if conf >= 0.65:
        return "moderate"
    return "low"


def generate_answer(filter_dict, results, diagnosis, event_type=None):
    """
    Build a natural-language answer string.

    Args:
        filter_dict: dict from parse_query().
        results:     list of result dicts from search() or find_transition_events().
        diagnosis:   dict from diagnose_no_match(), or None when results are non-empty.
        event_type:  "disappear" | "reappear" | None.

    Returns:
        str — a conversational answer ready for the UI.
    """
    class_name = filter_dict.get('class_name') or 'object'
    color = filter_dict.get('color')
    target_color = filter_dict.get('spatial_target_color')

    # Build a readable subject phrase, e.g. "red car", "person", "object"
    subject = f"{color} {class_name}" if color else class_name

    # ── ZERO RESULTS ──────────────────────────────────────────────────
    if not results:
        return _zero_results_answer(filter_dict, diagnosis, event_type, subject, class_name)

    # ── EVENT RESULTS (disappear / reappear) ──────────────────────────
    if event_type:
        return _event_answer(results, event_type, class_name)

    # ── POSITIVE FILTER-SEARCH RESULTS ────────────────────────────────
    return _search_answer(results, filter_dict, subject, target_color)


# ──────────────────────────────────────────────────────────────────────
# Private helpers
# ──────────────────────────────────────────────────────────────────────

def _zero_results_answer(filter_dict, diagnosis, event_type, subject, class_name):
    """Handle all zero-result cases."""

    if diagnosis is None:
        return f"No matches found for '{subject}' in this video."

    diag_type = diagnosis.get('type', '')

    # 1. Unsupported vocabulary
    if diag_type == 'unsupported_vocabulary':
        terms = diagnosis.get('terms', [])
        term_str = ", ".join(f"'{t}'" for t in terms)
        return (
            f"I can't detect {term_str} — that's outside the object classes "
            f"I was trained on. Try rephrasing with everyday objects like "
            f"person, car, bottle, backpack, etc."
        )

    # 2. Event — class never detected
    if diag_type == 'no_event':
        if event_type == 'disappear':
            return (
                f"I didn't see any {class_name} disappear. Either the "
                f"{class_name} was visible the whole time, or I never "
                f"detected one in this video at all."
            )
        else:
            return (
                f"I didn't find any reappearance of {class_name}. Either "
                f"it stayed visible throughout, or it was never detected."
            )

    # 3. Constraint failures
    if diag_type == 'constraint_failures':
        failures = diagnosis.get('failures', [])
        hints = diagnosis.get('hints', [])

        parts = []
        for f in failures:
            parts.append(f)

        msg = ". ".join(parts) if parts else f"No matches for '{subject}'"

        if hints:
            msg += ". " + " ".join(hints)

        return msg

    # Fallback
    return diagnosis.get('message', f"No results found for '{subject}'.")


def _event_answer(results, event_type, class_name):
    """Narrate disappear/reappear events."""

    if len(results) == 1:
        r = results[0]
        t = _fmt_time(r['start'])
        if event_type == 'disappear':
            return (
                f"The {class_name} disappeared around {t} — it was visible "
                f"before that and then dropped out of frame."
            )
        else:
            return (
                f"The {class_name} reappeared at {t} after being out of "
                f"frame for a while."
            )

    # Multiple events
    times = [_fmt_time(r['start']) for r in results]
    verb = "disappeared" if event_type == 'disappear' else "reappeared"

    if len(times) == 2:
        time_str = f"{times[0]} and {times[1]}"
    else:
        time_str = ", ".join(times[:-1]) + f", and {times[-1]}"

    return (
        f"The {class_name} {verb} {len(results)} times — at {time_str}."
    )


def _search_answer(results, filter_dict, subject, target_color):
    """Narrate positive filter-search results."""

    count = len(results)
    spatial = filter_dict.get('spatial')

    # Describe the spatial action if present
    action = ""
    if spatial:
        parts = spatial.split(':')
        if len(parts) == 2:
            rel, target = parts
            rel_phrase = {
                'touching': 'touching',
                'left_of':  'to the left of',
                'right_of': 'to the right of',
            }.get(rel, rel)
            target_desc = f"{target_color} {target}" if target_color else target
            action = f" {rel_phrase} the {target_desc}"

    # Confidence from the first result
    conf_label = _confidence_label(results[0].get('explanation', ''))

    if count == 1:
        t = _fmt_time(results[0]['start'])
        return (
            f"Found the {subject}{action} once, at {t} "
            f"({conf_label} confidence)."
        )

    # Multiple results — summarize with time range
    first_t = _fmt_time(results[0]['start'])
    last_t = _fmt_time(results[-1]['start'])

    if count == 2:
        return (
            f"Found the {subject}{action} at two points — {first_t} "
            f"and {last_t} ({conf_label} confidence)."
        )

    if count <= 5:
        mid_times = [_fmt_time(r['start']) for r in results[1:-1]]
        mid_str = ", ".join(mid_times)
        return (
            f"Found the {subject}{action} {count} times — first at "
            f"{first_t}, then at {mid_str}, and last at {last_t} "
            f"({conf_label} confidence)."
        )

    # Many results — just summarize range
    return (
        f"Found the {subject}{action} {count} times, spanning from "
        f"{first_t} to {last_t} ({conf_label} confidence)."
    )
