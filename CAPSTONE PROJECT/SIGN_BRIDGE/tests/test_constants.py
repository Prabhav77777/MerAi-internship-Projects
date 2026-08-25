import unittest
from constants import static_supported_letters


class TestConstants(unittest.TestCase):
    def test_static_supported_letters_sorts_valid_letters(self):
        self.assertEqual(static_supported_letters(["Z", "A", "J", "C"]), ("A", "C", "J", "Z"))

    def test_static_supported_letters_ignores_invalid_labels(self):
        self.assertEqual(static_supported_letters(["A", "AA", "1", None]), ("A",))


if __name__ == "__main__":
    unittest.main()
