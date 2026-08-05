import sys
import os

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.query.parser import parse_query

def main():
    queries = [
        "red car",
        "person without a helmet",
        "person without a backpack",
        "person with no helmet",
        "person having no helmet",
        "person left of the car",
        "person to the left of the car",
        "more than two people",
        "less than 5 ladies",
        "redcar",
        "blue gentleman wearing no hat",
        "find the red helicopters"
    ]
    
    all_passed = True

    for i, q in enumerate(queries, 1):
        parsed = parse_query(q)
        print(f"Test {i}: '{q}'")
        print(f"Parsed: {parsed}")
        print("-" * 60)
        
        # Every non-event query MUST have event=None
        assert parsed.get('event') is None, f"Non-event query got event={parsed.get('event')} in '{q}'"
        
        # Simple sanity check assertions
        if "red car" in q or "redcar" in q:
            assert parsed['class_name'] == 'car', f"Failed class_name in {q}"
            assert parsed['color'] == 'red', f"Failed color in {q}"
            assert not parsed['unsupported_terms'], f"Failed unsupported_terms in {q}"
        elif "helmet" in q:
            assert parsed['class_name'] == 'person', f"Failed class_name in {q}"
            assert 'helmet' not in parsed['exclude'], f"Failed exclude in {q}"
            assert 'helmet' in parsed['unsupported_terms'], f"Failed unsupported_terms in {q}"
        elif "backpack" in q:
            assert parsed['class_name'] == 'person', f"Failed class_name in {q}"
            assert 'backpack' in parsed['exclude'], f"Failed exclude in {q}"
            assert not parsed['unsupported_terms'], f"Failed unsupported_terms in {q}"
        elif "left of" in q:
            assert parsed['class_name'] == 'person', f"Failed class_name in {q}"
            assert parsed['spatial'] == 'left_of:car', f"Failed spatial in {q}"
        elif "two people" in q:
            assert parsed['class_name'] == 'person', f"Failed class_name in {q}"
            assert parsed['count_op'] == '>', f"Failed count_op in {q}"
            assert parsed['count_val'] == 2, f"Failed count_val in {q}"
        elif "ladies" in q:
            assert parsed['class_name'] == 'person', f"Failed class_name in {q}"
            assert parsed['count_op'] == '<', f"Failed count_op in {q}"
            assert parsed['count_val'] == 5, f"Failed count_val in {q}"
        elif "gentleman" in q:
            assert parsed['class_name'] == 'person', f"Failed class_name in {q}"
            assert parsed['color'] == 'blue', f"Failed color in {q}"
            assert 'hat' not in parsed['exclude'], f"Failed exclude in {q}"
            assert 'hat' in parsed['unsupported_terms'], f"Failed unsupported_terms in {q}"
        elif "helicopters" in q:
            assert parsed['class_name'] is None, f"Failed class_name in {q}"
            assert 'helicopters' in parsed['unsupported_terms'], f"Failed unsupported_terms in {q}"

    print(f"\nAll {len(queries)} existing tests passed (all have event=None).\n")
    print("=" * 60)
    print("EVENT DETECTION TESTS")
    print("=" * 60)

    # --- Event detection tests ---
    event_tests = [
        {
            "query": "when did the person disappear",
            "expect_event": "disappear",
            "expect_class": "person",
        },
        {
            "query": "where did I vanish",
            "expect_event": "disappear",
            "expect_class": None,  # "I" is a stopword, no COCO class
        },
        {
            "query": "person went behind the tree",
            "expect_event": "disappear",
            "expect_class": "person",  # "tree" is not COCO, only person matters
        },
        {
            "query": "when does the car reappear",
            "expect_event": "reappear",
            "expect_class": "car",
        },
    ]

    for i, t in enumerate(event_tests, 1):
        parsed = parse_query(t["query"])
        print(f"\nEvent Test {i}: '{t['query']}'")
        print(f"  Parsed: {parsed}")

        assert parsed["event"] == t["expect_event"], \
            f"  FAIL: expected event={t['expect_event']}, got {parsed['event']}"
        assert parsed["class_name"] == t["expect_class"], \
            f"  FAIL: expected class_name={t['expect_class']}, got {parsed['class_name']}"
        # Event queries must not carry filter constraints
        assert parsed["color"] is None, f"  FAIL: event query has color={parsed['color']}"
        assert parsed["spatial"] is None, f"  FAIL: event query has spatial={parsed['spatial']}"
        assert parsed["count_op"] is None, f"  FAIL: event query has count_op={parsed['count_op']}"
        assert parsed["exclude"] == [], f"  FAIL: event query has exclude={parsed['exclude']}"

        print(f"  PASS")

    print(f"\nAll {len(event_tests)} event detection tests passed!")
    print(f"\nGrand total: {len(queries) + len(event_tests)} tests — ALL PASSED")

if __name__ == "__main__":
    main()
