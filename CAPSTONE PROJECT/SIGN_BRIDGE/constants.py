"""Shared, conservative configuration for SignBridge's static classifier."""

# J and Z are motion-based ASL fingerspelling letters. A single image/frame
# cannot validate their motion path, so they are intentionally not active
# classifier targets even if historic data happens to contain either label.
DYNAMIC_ASL_LETTERS = frozenset()
ALL_ASL_LETTERS = tuple(chr(code) for code in range(ord("A"), ord("Z") + 1))


def static_supported_letters(model_classes):
    """Return sorted static targets represented by a loaded classifier."""
    return tuple(
        letter
        for letter in sorted(str(label).upper() for label in model_classes)
        if len(letter) == 1 and letter.isalpha()
    )

