"""Shared configuration for SignBridge's static classifier (supporting full A-Z alphabet)."""

# All letters A through Z are active classifier targets.
DYNAMIC_ASL_LETTERS = frozenset()


def static_supported_letters(model_classes):
    """Return sorted static targets represented by a loaded classifier."""
    return tuple(
        letter
        for letter in sorted(str(label).upper() for label in model_classes)
        if len(letter) == 1 and letter.isalpha() and letter not in DYNAMIC_ASL_LETTERS
    )

