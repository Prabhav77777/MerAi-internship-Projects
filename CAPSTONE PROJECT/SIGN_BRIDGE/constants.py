"""Shared configuration for SignBridge's static classifier."""

# Dynamic motion letters filter (empty to allow all 26 letters A-Z in static classifier)
DYNAMIC_ASL_LETTERS = frozenset()

# Full alphabet tuple (A-Z)
ALL_ASL_LETTERS = tuple(chr(code) for code in range(ord("A"), ord("Z") + 1))


def static_supported_letters(model_classes):
    """Return sorted static targets represented by a loaded classifier."""
    return tuple(
        letter
        for letter in sorted(str(label).upper() for label in model_classes)
        if len(letter) == 1 and letter.isalpha() and letter not in DYNAMIC_ASL_LETTERS
    )
