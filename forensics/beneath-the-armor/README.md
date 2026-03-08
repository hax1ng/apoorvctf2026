# Beneath The Armor

**Category:** Forensics | **Difficulty:** Hard (500 pts) | **Flag:** `apoorvctf{m0dul4r_4r17hm371c_15_fun_y34h}`

## Overview
A PNG image of Iron Man with data hidden using a multi-bit cross-channel LSB steganography technique.

## Solution
The challenge provides an Iron Man PNG image and hints: *"History repeats itself, even for ironman, life goes on cycles."*

Standard stego tools (zsteg, steghide, stegano) all fail because they extract the **same bit position** from each color channel. The trick here is that the data is hidden using **different bit positions per channel**:

- **Red channel**: bit 0 (LSB)
- **Green channel**: bit 1 (second bit)
- **Blue channel**: bit 2 (third bit)

The bits cycle through positions 0→1→2 across R→G→B, which is the "cycles" the hint refers to. The flag content (`m0dul4r_4r17hm371c_15_fun_y34h`) confirms this — modular arithmetic is the underlying concept.

To extract, read 3 bits per pixel (one from each channel at its respective bit position), pack them into bytes:

```python
from PIL import Image
import numpy as np

img = np.array(Image.open('challenge.png'))
bits = []
for y in range(img.shape[0]):
    for x in range(img.shape[1]):
        bits.append((int(img[y,x,0]) >> 0) & 1)  # R bit 0
        bits.append((int(img[y,x,1]) >> 1) & 1)  # G bit 1
        bits.append((int(img[y,x,2]) >> 2) & 1)  # B bit 2
data = bytes(np.packbits(np.array(bits[:len(bits)//8*8], dtype=np.uint8)))
print(data[:50])
```

## Key Takeaways
- Standard LSB tools only check the same bit position across all channels. When different bit positions are used per channel, you need custom extraction.
- Always try cross-channel bit combinations (R bit N, G bit M, B bit K for various N,M,K) when standard tools fail.
- Challenge hints are important: "cycles" and "modular arithmetic" pointed to the cycling bit positions.
- This technique evades zsteg's `-a` exhaustive scan because it doesn't enumerate cross-channel bit position combinations.
