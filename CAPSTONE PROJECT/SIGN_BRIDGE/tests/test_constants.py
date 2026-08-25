from constants import static_supported_letters


def test_static_supported_letters_removes_motion_letters_and_sorts():
    assert static_supported_letters(["Z", "A", "J", "C"]) == ("A", "C")


def test_static_supported_letters_ignores_invalid_labels():
    assert static_supported_letters(["A", "AA", "1", None]) == ("A",)
