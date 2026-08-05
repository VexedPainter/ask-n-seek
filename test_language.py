"""
Test suite for backend.nlp.language — detection, translation, and failure handling.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')

from unittest.mock import patch, MagicMock
from backend.nlp.language import detect_language, translate_to_english, translate_from_english

PASS_COUNT = 0
FAIL_COUNT = 0


def check(label, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    status = "PASS" if condition else "FAIL"
    if condition:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
    print(f"  [{status}] {label}")
    if detail:
        print(f"         {detail}")


# ─────────────────────────────────────────────────────────
# 1. Language detection (offline)
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("LANGUAGE DETECTION (offline)")
print("=" * 60)

# Kannada
kn_text = "ಕೆಂಪು ಕಾರ್ ಎಲ್ಲಿದೆ"
kn_lang = detect_language(kn_text)
check(f"Kannada detection: '{kn_text}'", kn_lang == 'kn', f"detected: {kn_lang}")

# Hindi
hi_text = "लाल कार कहाँ है"
hi_lang = detect_language(hi_text)
check(f"Hindi detection: '{hi_text}'", hi_lang == 'hi', f"detected: {hi_lang}")

# English
en_text = "where is the red car"
en_lang = detect_language(en_text)
check(f"English detection: '{en_text}'", en_lang == 'en', f"detected: {en_lang}")

# Short / ambiguous text should not crash
short_lang = detect_language("a")
check("Very short text does not crash", isinstance(short_lang, str), f"detected: {short_lang}")


# ─────────────────────────────────────────────────────────
# 2. Translation to English (online)
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TRANSLATION TO ENGLISH (online)")
print("=" * 60)

# Kannada -> English
kn_translated, kn_ok = translate_to_english(kn_text, 'kn')
check(
    f"Kannada -> English: '{kn_text}'",
    kn_ok and isinstance(kn_translated, str) and len(kn_translated) > 0,
    f"translated: '{kn_translated}' (success={kn_ok})"
)

# Hindi -> English
hi_translated, hi_ok = translate_to_english(hi_text, 'hi')
check(
    f"Hindi -> English: '{hi_text}'",
    hi_ok and isinstance(hi_translated, str) and len(hi_translated) > 0,
    f"translated: '{hi_translated}' (success={hi_ok})"
)

# English -> English (passthrough)
en_translated, en_ok = translate_to_english(en_text, 'en')
check(
    "English -> English passthrough",
    en_ok and en_translated == en_text,
    f"returned: '{en_translated}'"
)


# ─────────────────────────────────────────────────────────
# 3. Translation from English (online)
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TRANSLATION FROM ENGLISH (online)")
print("=" * 60)

en_answer = "Found the red car at 0:04"

# English -> Kannada
kn_answer, kn_ans_ok = translate_from_english(en_answer, 'kn')
check(
    f"English -> Kannada: '{en_answer}'",
    kn_ans_ok and isinstance(kn_answer, str) and len(kn_answer) > 0,
    f"translated: '{kn_answer}' (success={kn_ans_ok})"
)

# English -> Hindi
hi_answer, hi_ans_ok = translate_from_english(en_answer, 'hi')
check(
    f"English -> Hindi: '{en_answer}'",
    hi_ans_ok and isinstance(hi_answer, str) and len(hi_answer) > 0,
    f"translated: '{hi_answer}' (success={hi_ans_ok})"
)

# English -> English passthrough
en_answer2, en_ans_ok = translate_from_english(en_answer, 'en')
check(
    "English -> English passthrough",
    en_ans_ok and en_answer2 == en_answer,
    f"returned: '{en_answer2}'"
)


# ─────────────────────────────────────────────────────────
# 4. Graceful failure (simulated network error)
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("GRACEFUL FAILURE (mocked network error)")
print("=" * 60)

# Mock GoogleTranslator to raise an exception
mock_translator = MagicMock()
mock_translator.return_value.translate.side_effect = ConnectionError("Network is down")

with patch('backend.nlp.language.GoogleTranslator', mock_translator) if False else \
     patch.dict('sys.modules', {}):
    # Actually, let's patch at the import point inside the function
    pass

# Better approach: patch deep_translator.GoogleTranslator directly
with patch('deep_translator.GoogleTranslator') as mock_gt:
    mock_gt.return_value.translate.side_effect = ConnectionError("Simulated network failure")

    fail_text = "ಕೆಂಪು ಕಾರ್ ಎಲ್ಲಿದೆ"

    # translate_to_english should return original text + False
    result, success = translate_to_english(fail_text, 'kn')
    check(
        "translate_to_english graceful failure",
        not success and result == fail_text,
        f"returned: ('{result}', {success}) — original text preserved"
    )

    # translate_from_english should return original text + False
    result2, success2 = translate_from_english("Found red car", 'kn')
    check(
        "translate_from_english graceful failure",
        not success2 and result2 == "Found red car",
        f"returned: ('{result2}', {success2}) — original text preserved"
    )


# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print(f"TOTAL: {PASS_COUNT + FAIL_COUNT} tests — {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED")
print(f"{'=' * 60}")
