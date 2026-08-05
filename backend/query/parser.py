import re
import logging

logger = logging.getLogger(__name__)

COLORS = {"red", "blue", "green", "black", "white", "yellow", "gray", "orange", "silver", "brown", "pink", "purple", "cyan"}

SYNONYMS = {
    'woman': 'person', 'women': 'person',
    'man': 'person', 'men': 'person',
    'lady': 'person', 'ladies': 'person',
    'gentleman': 'person', 'gentlemen': 'person',
    'people': 'person',
    'vehicle': 'car', 'vehicles': 'car',
    'auto': 'car', 'automobile': 'car',
    'bike': 'bicycle', 'bikes': 'bicycle'
}

NUMBERS = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
}

COCO_CLASSES = {
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush"
}

def parse_query(text: str) -> dict:
    """
    Parses a natural language query into structured query parameters.
    This MVP version uses regex and keyword matching.
    Designed to be a drop-in replacement for a future NLP-based (e.g. spaCy) parser.
    
    Args:
        text (str): The natural language query.
        
    Returns:
        dict: A dictionary containing the parsed query parameters:
            - class_name (str or None): The primary object class (e.g., "car", "person").
            - color (str or None): The extracted color.
            - exclude (list of str): Objects that should NOT be present.
            - spatial (str or None): Spatial relationships (e.g., "left_of:car").
            - count_op (str or None): Operator for counting (">", "<", "==").
            - count_val (int or None): The numerical value for the count.
            - event (str or None): "disappear" or "reappear" for event queries.
    """
    result = {
        "class_name": None,
        "color": None,
        "exclude": [],
        "spatial": None,
        "count_op": None,
        "count_val": None,
        "event": None,
        "unsupported_terms": []
    }
    
    # 0. Normalization
    text = text.lower().strip()
    
    # 0.5 Event detection — MUST run before the negation regex so phrases
    #     like "disappeared" or "no longer visible" aren't mangled.
    DISAPPEAR_PHRASES = [
        r'no longer visible', r'no longer see',
        r'went behind', r'hidden behind',
        r'disappear(?:ed)?', r'vanish(?:ed)?', r'gone',
    ]
    REAPPEAR_PHRASES = [
        r'show up again', r'appear again', r'visible again',
        r'reappear(?:ed)?', r'came back', r'come back',
    ]
    
    disappear_pat = r'\b(?:' + '|'.join(DISAPPEAR_PHRASES) + r')\b'
    reappear_pat  = r'\b(?:' + '|'.join(REAPPEAR_PHRASES) + r')\b'
    
    event_match = re.search(reappear_pat, text) or re.search(disappear_pat, text)
    if event_match:
        matched_text = event_match.group(0)
        # Determine which type
        if re.search(reappear_pat, matched_text):
            result["event"] = "reappear"
        else:
            result["event"] = "disappear"
        
        # Strip the event phrase from text so the class extractor sees clean nouns
        text = text[:event_match.start()] + text[event_match.end():]
        
        # Extract class_name from remaining text (reuse synonym + COCO validation)
        words = re.findall(r'\b[a-z]+\b', text)
        stopwords = {"a", "an", "the", "some", "any", "is", "are", "of", "and",
                      "when", "where", "did", "does", "do", "i", "my", "me",
                      "what", "how", "behind", "from", "in", "to", "it"} | COLORS
        remaining = [w for w in words if w not in stopwords]
        
        def normalize_term(term):
            term = SYNONYMS.get(term, term)
            if term not in COCO_CLASSES and term.endswith('s') and term[:-1] in COCO_CLASSES:
                return term[:-1]
            if term not in COCO_CLASSES and term.endswith('es') and term[:-2] in COCO_CLASSES:
                return term[:-2]
            return term
        
        if remaining:
            for candidate in remaining:
                norm = normalize_term(candidate)
                if norm in COCO_CLASSES:
                    result["class_name"] = norm
                    break
            # If no valid COCO class found, record unsupported but don't block
            if result["class_name"] is None:
                for candidate in remaining:
                    norm = normalize_term(candidate)
                    if norm not in COCO_CLASSES:
                        result["unsupported_terms"].append(candidate)
        
        # Event queries are a different query type — skip filter parsing
        return result
    
    # 1. Compound splitting (e.g. "redcar" -> "red car")
    for c in COLORS:
        text = re.sub(rf'\b({c})([a-z]+)\b', r'\1 \2', text)
        
    # 2. Exclusions
    # Normalize varied phrasings to "without"
    text = re.sub(r'\b(with no|having no|wearing no|zero|0)\b', 'without', text)
    # Also handle standalone "no <noun>" at the start or anywhere, but be careful not to replace "no" inside words.
    text = re.sub(r'\bno\b', 'without', text)
    
    # Match "without [a/an/the] <noun>"
    exclude_matches = re.finditer(r'\bwithout\s+(?:a\s+|an\s+|the\s+)?([a-z]+)\b', text)
    for m in exclude_matches:
        result["exclude"].append(m.group(1))
    # Remove exclusion parts from text so they don't confuse later parsing
    text = re.sub(r'\bwithout\s+(?:a\s+|an\s+|the\s+)?[a-z]+\b', '', text)
    
    # 3. Spatial relations
    colors_str = '|'.join(COLORS)
    
    spatial_match = re.search(rf'\b(?:to the\s+)?(left|right)\s+of\s+(?:the\s+|a\s+|an\s+)?(?:({colors_str})\s+)?(?:colou?r(?:ed)?\s+)?([a-z]+)\b', text)
    if spatial_match:
        direction = spatial_match.group(1)
        target_color = spatial_match.group(2)
        target = spatial_match.group(3)
        
        target = SYNONYMS.get(target, target)
        result["spatial"] = f"{direction}_of:{target}"
        if target_color:
            result["spatial_target_color"] = target_color
            
        text = text[:spatial_match.start()] + text[spatial_match.end():]
        
    touch_match = re.search(rf'\b(touching|grabbing|pulling|holding|barging at|opening)\s+(?:the\s+|a\s+|an\s+)?(?:({colors_str})\s+)?(?:colou?r(?:ed)?\s+)?([a-z]+)\b', text)
    if touch_match:
        target_color = touch_match.group(2)
        target = touch_match.group(3)
        
        target = SYNONYMS.get(target, target)
        result["spatial"] = f"touching:{target}"
        if target_color:
            result["spatial_target_color"] = target_color
            
        text = text[:touch_match.start()] + text[touch_match.end():]

    # 4. Count operators
    count_pattern = r'\b(more than|greater than|less than|fewer than|exactly)\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b'
    count_match = re.search(count_pattern, text)
    if count_match:
        op_str = count_match.group(1)
        val_str = count_match.group(2)
        
        if op_str in ['more than', 'greater than']:
            result['count_op'] = '>'
        elif op_str in ['less than', 'fewer than']:
            result['count_op'] = '<'
        else:
            result['count_op'] = '=='
            
        result['count_val'] = NUMBERS.get(val_str, int(val_str) if val_str.isdigit() else None)
        # Remove count part from text
        text = text[:count_match.start()] + text[count_match.end():]
        
    # 5. Extract colors
    words = [w for w in re.findall(r'\b[a-z]+\b', text)]
    for w in words:
        if w in COLORS:
            result['color'] = w
            
    # 6. Extract class_name
    # Filter out stopwords and known colors to find the main noun
    stopwords = {"a", "an", "the", "some", "any", "is", "are", "of", "and"} | COLORS
    remaining = [w for w in words if w not in stopwords]
    
    if remaining:
        # Pick the last noun in the phrase as the class name
        raw_class = remaining[-1]
        result['class_name'] = SYNONYMS.get(raw_class, raw_class)

    # 7. Validation against COCO classes
    def normalize_term(term):
        term = SYNONYMS.get(term, term)
        if term not in COCO_CLASSES and term.endswith('s') and term[:-1] in COCO_CLASSES:
            return term[:-1]
        if term not in COCO_CLASSES and term.endswith('es') and term[:-2] in COCO_CLASSES:
            return term[:-2]
        return term

    # Validate class_name
    if result["class_name"]:
        norm_class = normalize_term(result["class_name"])
        if norm_class not in COCO_CLASSES:
            result["unsupported_terms"].append(result["class_name"])
            result["class_name"] = None
        else:
            result["class_name"] = norm_class
            
    # Validate exclude
    valid_excludes = []
    for ex in result["exclude"]:
        norm_ex = normalize_term(ex)
        if norm_ex not in COCO_CLASSES:
            result["unsupported_terms"].append(ex)
        else:
            valid_excludes.append(norm_ex)
    result["exclude"] = valid_excludes

    return result
