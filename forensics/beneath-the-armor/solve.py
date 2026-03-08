#!/usr/bin/env python3
"""Beneath The Armor - Multi-bit cross-channel LSB extraction"""

from PIL import Image
import numpy as np

img = np.array(Image.open('challenge.png'))
h, w = img.shape[:2]

# Extract: bit 0 from R, bit 1 from G, bit 2 from B
# 3 bits per pixel, interleaved
bits = []
for y in range(h):
    for x in range(w):
        bits.append((int(img[y, x, 0]) >> 0) & 1)  # R bit 0
        bits.append((int(img[y, x, 1]) >> 1) & 1)  # G bit 1
        bits.append((int(img[y, x, 2]) >> 2) & 1)  # B bit 2
        if len(bits) >= 8 * 500:
            break
    if len(bits) >= 8 * 500:
        break

n_bytes = len(bits) // 8
data = bytes(np.packbits(np.array(bits[:n_bytes * 8], dtype=np.uint8)))

# Find and print the flag
idx = data.find(b'apoorvctf{')
if idx != -1:
    end = data.find(b'}', idx)
    flag = data[idx:end + 1].decode()
    print(f"Flag: {flag}")
else:
    print("Flag not found")
