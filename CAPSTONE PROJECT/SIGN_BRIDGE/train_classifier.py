"""
train_classifier.py

Trains a simple classifier that maps 63 hand-landmark numbers -> a letter.
Run this after collect_data.py has produced data/landmarks.csv.

Why RandomForest instead of a neural net?
- Only 63 numeric features per sample (not raw pixels), so a tree-based
  model trains in seconds and works great at this scale.
- No GPU needed, trivial to deploy on Streamlit Community Cloud.

Output: model.pkl (loaded by the Streamlit app at inference time)
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

DATA_PATH = "data/landmarks.csv"
MODEL_OUT = "model.pkl"


def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} samples across {df['label'].nunique()} letters")

    X = df.drop(columns=["label"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X_train, y_train)

    print("\n--- Evaluation on held-out test set ---")
    preds = clf.predict(X_test)
    print(classification_report(y_test, preds))

    joblib.dump(clf, MODEL_OUT)
    print(f"\nModel saved to {MODEL_OUT}")


if __name__ == "__main__":
    main()