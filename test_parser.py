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
            
    if all_passed:
        print("\nAll 12 tests passed successfully!")

if __name__ == "__main__":
    main()
