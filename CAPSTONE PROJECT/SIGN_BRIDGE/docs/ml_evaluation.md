# ML evaluation

## Audited snapshot

- `data/landmarks.csv`: 86 rows, 63 features plus label; A–O with counts A 5, B 11, C 8, D 4, E 6, F 9, G 1, H 6, I 6, J 4, K 2, L 2, M 9, N 7, O 6.
- `model.pkl`: 200-tree Random Forest, 63 inputs, classes A–O.
- Representation: MediaPipe 21 `(x,y,z)` points, wrist-relative and divided by wrist-to-landmark-9 scale.
- Integrity: 17 exact duplicate rows, 18 duplicate feature vectors, and one conflicting duplicate feature vector.

## Reproducible diagnostic

`train_test_split(test_size=.2, random_state=42)` is non-stratified because G has one sample. A 200-tree Random Forest on that exact split produced train/test 68/18, accuracy **0.7778**, weighted precision **0.7944**, recall **0.7778**, and F1 **0.7599**. No test label was unseen in this seed.

This tiny duplicate-containing split is diagnostic, not justification for a 97% claim. Run `python train_classifier.py` to reproduce the method. Candidate training excludes J/Z; replacement requires a participant-disjoint, class-balanced comparison against the active artifact.
