"""
word_suggest.py
Offline word-autocomplete suggestions based on the letters typed so far.
Uses pyspellchecker's bundled frequency dictionary — no internet call
needed, so this is instant and doesn't touch your Gemini quota at all.
"""

from spellchecker import SpellChecker

_spell = SpellChecker()
_all_words = list(_spell.word_frequency.dictionary.keys())


def suggest_words(prefix: str, top_n: int = 5):
    """
    prefix: the letters spelled so far, e.g. "hel"
    returns: list of up to top_n likely words, most common first,
             e.g. ["help", "hell", "helping", "helped", "held"]
    """
    prefix = prefix.lower().strip()
    if not prefix:
        return []

    matches = [w for w in _all_words if w.startswith(prefix)]
    matches.sort(key=lambda w: -_spell.word_frequency.dictionary[w])
    return matches[:top_n]