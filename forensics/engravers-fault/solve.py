#!/usr/bin/env python3
"""
Engraver's Fault - Forensics CTF Challenge Solver

The challenge hides a binary message in JPEG DCT coefficients.
Modified images have their ±1 AC DCT coefficients reduced (F5-like stego),
creating a detectable "fingerprint". Each numbered image (105-352) represents
one bit: modified = 0, clean = 1.

Key insight: File 336 is a sparse image (80% zeros) where the ±1/±2 ratio
gives a misleading "clean" reading (0.2263). The ±2/±3 ratio (2.15 vs 2.96+
for truly clean files) reveals it IS modified. Using a combined metric
correctly classifies all 248 files.
"""

import jpegio
import numpy as np
from collections import Counter
import os
import sys

GALLERY = "chal1/chal1/gallery"

def get_ratios(filepath):
    """Calculate ±1/±2 and ±2/±3 AC DCT coefficient ratios."""
    img = jpegio.read(filepath)
    dct = img.coef_arrays[0]  # Luminance component
    ac = dct.copy()
    ac[::8, ::8] = 0  # Zero out DC coefficients
    flat = ac.flatten()
    hist = Counter(flat)
    ones = hist.get(1, 0) + hist.get(-1, 0)
    twos = hist.get(2, 0) + hist.get(-2, 0)
    threes = hist.get(3, 0) + hist.get(-3, 0)
    r12 = ones / (twos + 1)
    r23 = twos / (threes + 1)
    return r12, r23

def is_modified(r12, r23):
    """Classify image as modified using combined metric.

    Primary: r12 < 0.15 → clearly modified
    Secondary: r12 < 0.25 AND r23 < 2.5 → modified sparse image
    (handles edge case where sparse images have artificially high r12)
    """
    if r12 < 0.15:
        return True
    if r12 < 0.25 and r23 < 2.5:
        return True
    return False

def main():
    gallery_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), GALLERY)

    # Extract bits from files 105-352 (248 files = 31 bytes)
    bits = []
    for i in range(105, 353):
        filepath = os.path.join(gallery_path, f"{i}.jpg")
        r12, r23 = get_ratios(filepath)
        bit = 0 if is_modified(r12, r23) else 1
        bits.append(bit)

    # Decode 8-bit ASCII
    bitstr = ''.join(str(b) for b in bits)
    message = ''
    for i in range(0, len(bitstr) - 7, 8):
        byte = int(bitstr[i:i+8], 2)
        message += chr(byte)

    flag = f"apoorvctf{{{message.rstrip('}')}}}".replace("}}", "}")
    print(f"Flag: {flag}")
    print(f"Decoded message: {message}")

if __name__ == "__main__":
    main()
