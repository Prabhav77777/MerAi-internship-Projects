"""
tests/test_pipeline.py

Unit test suite for SignBridge core components:
1. OpenCV image conversion & landmark extraction interface
2. Static supported letter configuration
3. Classifier loading and prediction interface
4. Offline word suggestion engine
5. Gemini fallback resilience
"""

import unittest
import numpy as np
import cv2

from constants import ALL_ASL_LETTERS, static_supported_letters
from hand_utils import extract_landmarks_from_bgr, bytes_to_bgr_image
from word_suggest import suggest_words
from gemini_helper import clean_sentence
from classify import predict_letter, get_supported_letters, load_model


class TestSignBridgePipeline(unittest.TestCase):
    def test_bytes_to_bgr_image_conversion(self):
        """Test converting raw JPEG/PNG image bytes into an OpenCV BGR matrix."""
        # Create a dummy 100x100 RGB image and encode to JPEG bytes
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, encoded = cv2.imencode(".jpg", dummy_img)
        img_bytes = encoded.tobytes()

        bgr_mat = bytes_to_bgr_image(img_bytes)
        self.assertIsNotNone(bgr_mat)
        self.assertEqual(bgr_mat.shape, (100, 100, 3))

    def test_static_supported_letters_filtering(self):
        """Test static_supported_letters sorts and filters correctly."""
        self.assertEqual(ALL_ASL_LETTERS[0], "A")
        self.assertEqual(ALL_ASL_LETTERS[-1], "Z")
        self.assertEqual(len(ALL_ASL_LETTERS), 26)

        mock_classes = ["Z", "A", "1", "C", "AA", None]
        supported = static_supported_letters(mock_classes)
        self.assertEqual(supported, ("A", "C", "Z"))

    def test_classifier_interface(self):
        """Test loaded Random Forest classifier returns valid prediction and probability."""
        model = load_model()
        self.assertIsNotNone(model)

        supported_letters = get_supported_letters()
        self.assertGreaterEqual(len(supported_letters), 14)

        # Test dummy 63-feature prediction
        dummy_features = [0.0] * 63
        letter, confidence = predict_letter(dummy_features)
        self.assertIn(letter, supported_letters)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_word_suggestions(self):
        """Test offline word prefix lookup."""
        sug_hel = suggest_words("hel")
        self.assertIn("help", sug_hel)

        sug_th = suggest_words("th")
        self.assertGreater(len(sug_th), 0)

    def test_gemini_fallback(self):
        """Test Gemini clean_sentence returns raw text gracefully when key unavailable."""
        raw_input = "HELO HW ARE YOU"
        result = clean_sentence(raw_input)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
