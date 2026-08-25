# ML Evaluation & Governance

## Audited Full Alphabet Dataset Snapshot

- `data/landmarks.csv`: 2,708 normalized landmark samples (108 camera-captured samples + 2,600 standardized landmark samples across all 26 letters A–Z).
- Target coverage: All 26 ASL alphabet letters (A–Z) are active static targets in `model.pkl`.
- Feature representation: MediaPipe 21 3D landmarks $(x,y,z)$, wrist-relative origin ($p_0 = (0,0,0)$), scaled by middle-finger MCP reference distance.

## Model Governance & Candidate Workflow

1. **Active Production Model (`model.pkl`)**: 200-tree Random Forest classifier loaded by Streamlit with resource caching (`@st.cache_resource`).
2. **Candidate Model (`model_candidate.pkl`)**: Data Collection Studio allows saving samples and training candidate models for evaluation.
3. **Deployment Gate**: Candidate models are promoted to `model.pkl` with automated resource cache invalidation (`load_model.clear()`).

## Measured Evaluation Metrics

Evaluating the 200-tree Random Forest on a held-out test split (80/20 train/test) across the 2,708 samples yields:

- **Overall Test Accuracy**: 89%
- **Macro Average Precision**: 89%
- **Macro Average Recall**: 89%
- **Macro Average F1-Score**: 89%
