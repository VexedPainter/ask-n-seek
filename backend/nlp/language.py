"""
Language detection and translation layer.

- detect_language() uses langdetect (pure Python, offline).
- translate_to_english() / translate_from_english() use deep-translator
  (Google Translate over HTTP — no local model, no GPU).
- All translation calls degrade gracefully: on any failure the original
  text is returned with success=False, never raising.
"""
import logging

logger = logging.getLogger(__name__)

# ── Detection (offline, no network) ──────────────────────────────────

def detect_language(text: str) -> str:
    """
    Detect the ISO-639-1 language code of *text*.

    Returns 'en' if detection fails or the text is too short to classify.
    """
    # Devanagari-script languages that langdetect often confuses with each other.
    # For our purposes they all translate fine via 'hi' (Hindi).
    DEVANAGARI_ALIASES = {'ne', 'mr', 'sa'}  # Nepali, Marathi, Sanskrit

    try:
        from langdetect import detect
        code = detect(text)
        if code in DEVANAGARI_ALIASES:
            code = 'hi'
        return code
    except Exception:
        # langdetect can throw LangDetectException on very short / ambiguous input
        return 'en'


# ── Translation (online, needs network) ──────────────────────────────

def translate_to_english(text: str, source_lang: str) -> tuple[str, bool]:
    """
    Translate *text* from *source_lang* into English.

    Returns:
        (translated_text, success)
        On ANY failure (network, timeout, API error) returns (original text, False).
    """
    if source_lang == 'en':
        return text, True

    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source=source_lang, target='en').translate(text)
        if translated:
            return translated, True
        return text, False
    except Exception as e:
        logger.warning("Translation to English failed for '%s' (%s): %s", text, source_lang, e)
        return text, False


def translate_from_english(text: str, target_lang: str) -> tuple[str, bool]:
    """
    Translate *text* from English into *target_lang*.

    Returns:
        (translated_text, success)
        On ANY failure returns (original English text, False).
    """
    if target_lang == 'en':
        return text, True

    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source='en', target=target_lang).translate(text)
        if translated:
            return translated, True
        return text, False
    except Exception as e:
        logger.warning("Translation from English failed for '%s' (%s): %s", text, target_lang, e)
        return text, False
