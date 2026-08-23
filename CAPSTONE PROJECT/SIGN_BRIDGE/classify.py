"""
classify.py
Loads model.pkl once and exposes a simple predict function used by the
Streamlit app.
"""

import os

import joblib
import numpy as np
import streamlit as st

MODEL_PATH = "model.pkl"


@st.cache_resource
def load_model():
    """Loads the trained RandomForest classifier, with graceful error
    handling if the model file is missing or incompatible."""
    if not os.path.exists(MODEL_PATH):
        st.error(
            f"Model file `{MODEL_PATH}` not found. "
            "Please run `python train_classifier.py` first to train the model."
        )
        return None

    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None


def predict_letter(landmarks):
    """
    landmarks: list of 63 floats from hand_utils.extract_landmarks_from_bgr

    Returns: (predicted_letter: str, confidence: float 0-1)
             Returns (None, 0.0) if the model isn't loaded.
    """
    model = load_model()
    if model is None:
        return None, 0.0

    X = np.array(landmarks).reshape(1, -1)

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    confidence = max(probabilities)

    return prediction, confidence