# Author on the Run

**Category:** Forensics | **Difficulty:** 500 | **Flag:** `apoorvctf{ohyougotthisfardamn}`

## Overview
Keyboard acoustic side-channel attack: given a reference recording of each key (a-z) pressed 50 times and a recording of the flag being typed, decode the keystrokes.

## Solution

1. **File analysis**: Two mono 16-bit WAV files at 44100 Hz. Reference.wav is ~305 seconds (1300 keystrokes), flag.wav is ~12 seconds.

2. **Keystroke detection**: Used scipy `find_peaks` on an energy envelope (10ms sliding window) with `min_distance=175ms` and `threshold=3%` of max energy. Found exactly 1300 peaks in the reference and 19 in the flag.

3. **Feature extraction**: For each keystroke, extracted a 10ms window centered on the energy peak and computed 20 MFCCs (mean + std across time frames = 40-dimensional feature vector). The short 10ms window was critical — longer windows degraded accuracy by including ambient noise.

4. **Classification**: KNN matching (k=5) against all 1300 reference samples, with majority voting. The 1300 reference keystrokes were labeled in QWERTY order (first 50 = 'q', next 50 = 'w', etc.).

5. **Result**: Decoded to `ohyougotthisfardamn` = "oh you got this far damn"

Reference `solve2.py` for the full exploit code.

## Key Takeaways
- Keyboard acoustic emanation attacks work surprisingly well even with simple MFCC + KNN
- Window size around the keystroke peak matters enormously — 10ms beat 20-30ms
- Using individual samples (KNN) instead of averaged templates improves robustness
- The challenge description hints at the approach: "recording every keystroke" = acoustic side-channel
