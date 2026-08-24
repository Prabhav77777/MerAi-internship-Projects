# Prompt engineering

Gemini is intentionally post-processing only: camera → MediaPipe → Random Forest → text remains the reliable core. The system prompt gives Gemini a narrow SignBridge persona, permits correction of obvious recognition noise, and forbids invented content or explanatory prose.

The runtime prompt supplies dynamic context: raw fingerspelled text and the current word count. For example, `MY NME IS PRABHV` with four words can yield `My name is Prabhav.` The instruction preserves ambiguity conservatively and avoids expanding short input.

If the optional secret is absent or Gemini errors, the app returns raw text and continues. This protects core communication from key, quota, or network failures; users should still verify sensitive messages.
