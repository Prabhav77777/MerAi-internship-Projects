# SignBridge Audit Report

## CURRENTLY WORKING

✅ **Core Application Flow**
- Streamlit interface loads and responds correctly
- Three operational modes: Click, Live, and Data Collection Studio
- State management via st.session_state persists across interactions

✅ **MediaPipe Hand Landmarking**
- Automatic model download and caching
- 21-point hand landmark extraction with x,y,z coordinates
- Proper normalization (wrist origin, scale by middle finger MCP)
- Visual feedback with skeleton overlay

✅ **Machine Learning Pipeline**
- Random Forest classifier loads via joblib caching
- Returns predicted letter and confidence probability
- Handles missing model gracefully with user instructions

✅ **Click Mode**
- Single-frame photo capture via st.camera_input
- Hand detection and landmark extraction
- Prediction display with confidence metric
- Correction mechanism for misclassifications
- Sample saving to dataset on confirmation

✅ **Live Mode**
- WebRTC streaming with streamlit-webrtc integration
- Background video processing thread
- Stability detection (6-frame hold requirement)
- Auto-commit of letters when steady
- Visual feedback with progress bar and detection overlay

✅ **Data Collection Studio**
- Live camera feed with landmark overlay
- Target letter selection A-Z
- Sample saving functionality
- Dataset summary and statistics display
- One-click model retraining
- Dataset clearing capability

✅ **Word Suggestions**
- Offline dictionary lookup using pyspellchecker
- Real-time prefix-based completions
- Click-to-auto-complete functionality

✅ **Sentence Building**
- Letter buffering into current_word
- Word completion detection
- Sentence buffer accumulation
- Backspace, end-word, clear-word, reset-all controls

✅ **Gemini AI Integration**
- Secure API key management via Streamlit secrets
- Strict system prompt preventing hallucination
- Raw text fallback when API unavailable
- Sentence cleanup for punctuation/capitalization

✅ **Text-to-Speech**
- gTTS conversion to MP3 audio bytes
- In-memory audio playback (no temp files)
- Error handling for network failures

✅ **Data Management**
- CSV-based landmark dataset with header
- Sample appending for incremental learning
- Dataset statistics (total samples, unique letters)
- Samples-per-letter breakdown

✅ **Session Analytics**
- History log with timestamped letters
- Letter frequency visualization via ProgressColumn
- Dynamic data editor for history inspection

✅ **Video Extraction Tools**
- collect_from_video_file.py for arbitrary video files
- collect_full_alphabet_video.py for sequential alphabet tutorials
- Both interactive and automatic extraction modes
- Frame sampling to reduce redundancy

✅ **Model Training**
- train_classifier.py with train/test split
- Stratified sampling when possible
- Classification report output
- Model persistence via joblib

## CURRENTLY BROKEN

❌ **Live Mode Dependencies**
- Requires streamlit-webrtc which may not deploy correctly on all platforms
- No explicit check for WebRTC availability before attempting initialization
- Error handling shows warning but doesn't prevent UI rendering

❌ **J and Z Letter Handling**
- Documentation correctly states J & Z are motion-based and unsupported
- However, UI still allows selection of J/Z in Data Collection Studio
- No visual indication these letters won't work in recognition

❌ **Gemini Quota/Permission Issues**
- Falls back to raw text on any exception (good)
- But provides no way to reconfigure or test API key without restart
- No quota usage monitoring or warnings

❌ **Audio Playback Reliability**
- gTTS requires internet connection
- No local fallback or caching mechanism
- Silent failure (returns None) with only caption indication

## MISSING

🔸 **Confidence Threshold Adjustment**
- Live mode uses hardcoded CONFIDENCE_THRESHOLD = 0.45
- No UI control to adjust sensitivity for different lighting/conditions

🔸 **Stability Frame Configuration**
- Hardcoded STABILITY_FRAMES = 6 in multiple places
- No customization for different user motor control capabilities

🔸 **Cooldown Period Tuning**
- Fixed COOLDOWN_SECONDS = 1.0 prevents rapid same-letter entry
- Not adjustable for users who need faster/slower input

🔸 **Export/Import Functionality**
- No way to backup/share collected datasets
- No model export for use in other applications
- No session history export

🔸 **Advanced Modeling Options**
- Locked into Random Forest (no experimentation with other algorithms)
- No hyperparameter tuning interface
- No cross-validation visualization

🔸 **Multi-hand Support**
- Currently only processes first detected hand
- No handling for two-handed signs or interference rejection

🔸 **Performance Metrics**
- No display of processing latency/FPS
- No resource usage monitoring (CPU/memory during operation)
- No benchmarking tools

🔸 **Accessibility Features**
- No screen reader compatibility enhancements
- No high-contrast mode toggle
- No keyboard-only navigation improvements
- No adjustable UI scaling

🔸 **Error Recovery Guidance**
- When model missing, tells user to train but doesn't facilitate it
- No one-click training from error state
- No guided setup wizard for first-time users

🔸 **Multi-language Support**
- Hardcoded English for TTS and Gemini prompts
- No localization infrastructure
- No support for other sign language variants

## RISKY

⚠️ **Internet Dependencies**
- Gemini API requires internet and valid API key
- gTTS requires internet for speech synthesis
- WebRTC may face firewall/NAT issues in corporate environments
- No offline fallback modes for core functionality

⚠️ **Model Security**
- Random Forest model loaded via joblib (potential code execution risk if tampered)
- No model integrity verification
- No protection against malicious landmark data poisoning

⚠️ **Data Privacy**
- Landmark data includes sensitive hand geometry information
- No anonymization or encryption of collected samples
- Dataset could potentially be reversed to infer user characteristics

⚠️ **Rate Limiting & Quotas**
- Gemini API usage unbounded in UI (could exhaust free tier)
- No usage tracking, warnings, or hard limits
- gTTS also subject to Google usage policies

⚠️ **WebRTC Security**
- Browser-based real-time communication introduces attack surface
- Dependencies on external STUN/TURN servers
- No explicit content security policy for streamlit-webrtc

⚠️ **Medical Device Implications**
- Marketed as "assistive communication assistant"
- No disclaimers about not being a medical device
- No clinical validation or accuracy guarantees stated

## NEEDS IMPROVEMENT

🔧 **Code Organization**
- Duplicate constants (STABILITY_FRAMES, etc.) across files
- Some magic numbers could be named constants
- Long functions in app.py could be broken into components

🔧 **Error Handling & User Feedback**
- More specific error messages for different failure modes
- Loading states during model operations
- Better distinction between recoverable and fatal errors
- Retry mechanisms for transient failures

🔧 **Performance Optimization**
- Frame skipping in live mode could be made adaptive
- MediaPipe model loading could show progress
- Dataset operations on large CSRs could be paginated
- Consider lazy initialization for infrequently used features

🔧 **User Experience Improvements**
- Better onboarding/tutorial for first-time users
- Undo/redo functionality for sentence building
- Gesture-based controls (e.g., swipe to clear)
- Dark/light theme persistence
- Mobile-responsive layout improvements

🔧 **Data Quality & Validation**
- Outlier detection in collected landmarks
- Automatic detection of poor-quality samples
- Guidance for users on optimal hand positioning
- Confidence-based filtering during collection

🔧 **Testing & Validation**
- No unit tests visible in codebase
- No automated validation of core functions
- No test data sets for regression checking
- No CI/CD pipeline evidence

🔧 **Documentation & Maintainability**
- Inline comments could be more descriptive
- Public API docstrings for exported functions
- Architecture decision records (ADRs)
- Contributing guidelines visible

🔧 **Deployment Readiness**
- Dockerfile or deployment manifests not visible
- Health check endpoints missing
- Logging configuration not apparent
- Monitoring hooks absent

## SUMMARY

SignBridge demonstrates a thoughtful implementation of an ASL fingerspelling-to-speech system with strong core functionality. The modular architecture separates concerns well, and the human-in-the-loop feedback mechanism for continuous improvement is particularly notable.

Primary risks center around external service dependencies (Gemini, gTTS, WebRTC) and lack of offline fallbacks. The project would benefit from increased configurability, performance monitoring, and deployment hardening.

The code is generally clean and functional, though could use additional abstraction to reduce duplication and improve maintainability. As a capstone project, it successfully demonstrates end-to-end ML application development with consideration for real-world usability factors.