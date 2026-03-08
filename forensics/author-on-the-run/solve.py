#!/usr/bin/env python3
"""Keyboard acoustic side-channel attack solver.

Reference.wav: 26 keys (a-z in qwertyuiop order) each pressed 50 times.
flag.wav: unknown keystrokes to decode.
"""

import numpy as np
import wave
from scipy import signal
from collections import defaultdict

def read_wav(path):
    with wave.open(path, 'rb') as w:
        frames = w.readframes(w.getnframes())
        data = np.frombuffer(frames, dtype=np.int16).astype(np.float64)
        rate = w.getframerate()
    return data, rate

def find_keystrokes(data, rate, threshold_factor=0.3, min_gap_ms=80, window_ms=50):
    """Find keystroke positions using energy envelope."""
    # Compute energy envelope
    window_size = int(rate * window_ms / 1000)
    energy = np.convolve(data**2, np.ones(window_size)/window_size, mode='same')

    threshold = np.max(energy) * threshold_factor

    # Find regions above threshold
    above = energy > threshold

    # Find onset positions
    min_gap = int(rate * min_gap_ms / 1000)
    keystrokes = []
    i = 0
    while i < len(above):
        if above[i]:
            start = max(0, i - int(rate * 0.005))  # 5ms before onset
            # Find end of this keystroke region
            j = i
            while j < len(above) and above[j]:
                j += 1
            end = min(len(data), j + int(rate * 0.01))  # 10ms after
            keystrokes.append((start, end))
            i = j + min_gap  # skip min_gap
        else:
            i += 1

    return keystrokes

def extract_features(data, rate, start, end):
    """Extract spectral features from a keystroke segment."""
    # Use a fixed window around the keystroke peak
    segment = data[start:end]
    if len(segment) < 256:
        segment = np.pad(segment, (0, 256 - len(segment)))

    # FFT-based features
    # Use the first ~10ms around peak for the "hit" sound
    peak_idx = np.argmax(np.abs(segment))
    hit_start = max(0, peak_idx - int(rate * 0.002))
    hit_end = min(len(segment), peak_idx + int(rate * 0.015))
    hit = segment[hit_start:hit_end]

    if len(hit) < 256:
        hit = np.pad(hit, (0, 256 - len(hit)))

    # Compute MFCC-like features using FFT
    n_fft = 1024
    spectrum = np.abs(np.fft.rfft(hit, n=n_fft))

    # Log mel-like features (simple version using triangular filters)
    n_filters = 40
    freq_bins = len(spectrum)
    filters = np.zeros((n_filters, freq_bins))
    mel_points = np.linspace(0, freq_bins - 1, n_filters + 2).astype(int)
    for i in range(n_filters):
        start_bin = mel_points[i]
        center_bin = mel_points[i + 1]
        end_bin = mel_points[i + 2]
        for j in range(start_bin, center_bin):
            if center_bin != start_bin:
                filters[i, j] = (j - start_bin) / (center_bin - start_bin)
        for j in range(center_bin, end_bin):
            if end_bin != center_bin:
                filters[i, j] = (end_bin - j) / (end_bin - center_bin)

    mel_spectrum = np.dot(filters, spectrum)
    mel_spectrum = np.log(mel_spectrum + 1e-10)

    # Also add raw spectral shape
    # Downsample spectrum to fixed size
    n_spec = 64
    indices = np.linspace(0, len(spectrum) - 1, n_spec).astype(int)
    spec_features = np.log(spectrum[indices] + 1e-10)

    features = np.concatenate([mel_spectrum, spec_features])
    return features

def main():
    print("Loading audio files...")
    ref_data, rate = read_wav("Reference.wav")
    flag_data, _ = read_wav("flag.wav")

    print(f"Reference: {len(ref_data)} samples, {len(ref_data)/rate:.1f}s")
    print(f"Flag: {len(flag_data)} samples, {len(flag_data)/rate:.1f}s")

    # The keys are in QWERTY order: qwertyuiopasdfghjklzxcvbnm
    key_order = "qwertyuiopasdfghjklzxcvbnm"
    keys_per_letter = 50

    print("\nFinding keystrokes in reference...")
    ref_keystrokes = find_keystrokes(ref_data, rate, threshold_factor=0.15)
    print(f"Found {len(ref_keystrokes)} keystrokes in reference (expected {26*50}={26*50})")

    # If we didn't find exactly 1300, try adjusting threshold
    for tf in [0.1, 0.08, 0.05, 0.2, 0.25, 0.3]:
        if len(ref_keystrokes) == 1300:
            break
        ref_keystrokes = find_keystrokes(ref_data, rate, threshold_factor=tf)
        print(f"  threshold={tf}: found {len(ref_keystrokes)} keystrokes")

    if len(ref_keystrokes) != 1300:
        print(f"\nWARNING: Found {len(ref_keystrokes)} keystrokes, expected 1300")
        print("Trying different parameters...")
        for gap in [60, 100, 120, 150]:
            for tf in [0.05, 0.08, 0.1, 0.15, 0.2]:
                ks = find_keystrokes(ref_data, rate, threshold_factor=tf, min_gap_ms=gap)
                if len(ks) == 1300:
                    ref_keystrokes = ks
                    print(f"  Found 1300 with threshold={tf}, gap={gap}ms")
                    break
            if len(ref_keystrokes) == 1300:
                break

    # Build per-key templates
    print("\nBuilding key templates...")
    key_features = defaultdict(list)

    for i, (start, end) in enumerate(ref_keystrokes):
        key_idx = i // keys_per_letter
        if key_idx >= 26:
            break
        key = key_order[key_idx]
        feat = extract_features(ref_data, rate, start, end)
        key_features[key].append(feat)

    # Average features per key
    key_templates = {}
    for key, feats in key_features.items():
        key_templates[key] = np.mean(feats, axis=0)

    print(f"Built templates for {len(key_templates)} keys: {''.join(sorted(key_templates.keys()))}")

    # Find keystrokes in flag
    print("\nFinding keystrokes in flag...")
    flag_keystrokes = find_keystrokes(flag_data, rate, threshold_factor=0.15)
    print(f"Found {len(flag_keystrokes)} keystrokes in flag")

    # Try different thresholds if needed
    for tf in [0.1, 0.08, 0.05, 0.2]:
        if len(flag_keystrokes) > 5:
            break
        flag_keystrokes = find_keystrokes(flag_data, rate, threshold_factor=tf)
        print(f"  threshold={tf}: found {len(flag_keystrokes)} keystrokes")

    # Match each flag keystroke to closest template
    print("\nMatching flag keystrokes...")
    decoded = []
    for i, (start, end) in enumerate(flag_keystrokes):
        feat = extract_features(flag_data, rate, start, end)

        best_key = None
        best_dist = float('inf')
        for key, template in key_templates.items():
            dist = np.linalg.norm(feat - template)
            if dist < best_dist:
                best_dist = dist
                best_key = key

        decoded.append(best_key)

    result = ''.join(decoded)
    print(f"\nDecoded text: {result}")
    print(f"Flag: apoorvctf{{{result}}}")

    # Also try with cosine similarity
    print("\n--- Cosine similarity matching ---")
    decoded_cos = []
    for i, (start, end) in enumerate(flag_keystrokes):
        feat = extract_features(flag_data, rate, start, end)

        best_key = None
        best_sim = -float('inf')
        for key, template in key_templates.items():
            sim = np.dot(feat, template) / (np.linalg.norm(feat) * np.linalg.norm(template) + 1e-10)
            if sim > best_sim:
                best_sim = sim
                best_key = key

        decoded_cos.append(best_key)

    result_cos = ''.join(decoded_cos)
    print(f"Decoded text: {result_cos}")
    print(f"Flag: apoorvctf{{{result_cos}}}")

if __name__ == "__main__":
    main()
