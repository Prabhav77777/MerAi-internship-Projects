"""Shared configuration for SignBridge's static classifier (supporting full A-Z alphabet)."""

# All 26 letters A through Z are supported.
DYNAMIC_ASL_LETTERS = frozenset()
ALL_ASL_LETTERS = tuple(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def static_supported_letters(model_classes):
    """Return sorted targets represented by a loaded classifier."""
    return tuple(
        letter
        for letter in sorted(str(label).upper() for label in model_classes)
        if len(letter) == 1 and letter.isalpha() and letter not in DYNAMIC_ASL_LETTERS
    )

