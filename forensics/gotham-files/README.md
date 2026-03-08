# The Gotham Files

**Category:** Forensics | **Difficulty:** Easy-Medium | **Flag:** `apoorvctf{th3_c0m1cs_l13_1n_th3_PLTE}`

## Overview
A comic book PNG image with a flag hidden in the unused palette entries.

## Solution

The image is a paletted PNG (8-bit colormap) with two metadata hints:
- **Artist:** "The Collector"
- **Comment:** "Not all colors make it to the page. In Gotham, only the red light tells the truth."

The PNG uses a PLTE chunk with 256 palette entries, but only indices 0–199 are actually referenced by pixels. The remaining 56 entries (200–255) are unused — they "don't make it to the page."

Reading the **red channel values** of unused palette entries 200–236 as ASCII:

```
idx 200: R=97  → 'a'
idx 201: R=112 → 'p'
idx 202: R=111 → 'o'
...
idx 236: R=125 → '}'
```

This spells out: `apoorvctf{th3_c0m1cs_l13_1n_th3_PLTE}`

```python
from PIL import Image
img = Image.open('challenge.png')
palette = img.getpalette()
indices = set(np.array(img).flatten())
unused = [i for i in range(256) if i not in indices]
flag = ''.join(chr(palette[i*3]) for i in unused if 32 <= palette[i*3] <= 126)
print(flag)
```

## Key Takeaways
- Paletted PNGs can hide data in unused PLTE entries — always check which palette indices are actually referenced by pixels.
- Metadata comments are critical hints in forensics challenges.
- "PLTE" in the flag itself confirms the technique — the PNG PLTE chunk was the hiding spot.
