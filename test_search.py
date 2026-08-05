import sys
import os

from backend.query.parser import parse_query
from backend.search.search import search
from backend.search.no_match import diagnose_no_match

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
        "find the black helicopters",
        "orange car",
        "red frisbee"
    ]

    VIDEO_ID = "test_video_60s.mp4"

    for q in queries:
        print(f"Query: '{q}'")
        filter_dict = parse_query(q)
        # print(f"Parsed Filter: {filter_dict}")
        
        results = search(filter_dict, VIDEO_ID)
        
        if len(results) > 0:
            print(f"Results: {len(results)} matches found")
            for r in results:
                print(f"  - Window {r['window']}s: {r['explanation']}")
        else:
            print("Results: 0 matches found")
            diagnosis = diagnose_no_match(filter_dict, VIDEO_ID)
            print(f"Diagnosis: [{diagnosis['type']}] {diagnosis['message']}")
            
        print("-" * 60)

if __name__ == "__main__":
    main()
