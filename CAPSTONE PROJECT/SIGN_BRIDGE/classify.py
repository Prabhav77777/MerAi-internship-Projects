"""
classify.py
Loads model.pkl once and exposes a simple predict function used by the
Streamlit app.
"""

import joblib
import numpy as np
import streamlit as st

MODEL_PATH = "model.pkl"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


def predict_letter(landmarks):
    """
    landmarks: list of 63 floats from hand_utils.extract_landmarks_from_bgr

    Returns: (predicted_letter: str, confidence: float 0-1)
    """
    model = load_model()
    X = np.array(landmarks).reshape(1, -1)

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    confidence = max(probabilities)

    return prediction, confidence