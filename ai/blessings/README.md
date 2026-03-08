# Blessings

**Category:** AI/Misc | **Difficulty:** Medium | **Flag:** `apoorvctf{1_40_35}`

## Overview
Given an original and processed image plus two helper scripts, recover convolution kernels and compute their determinants.

## Solution

The challenge provides:
- `flower.jpg` — original image
- `flower_processed.npy` / `flower_processed.jpg` — the convolved result
- `retrieve_kernel.py` — recovers the 3x3 convolution kernel per RGB channel using least-squares regression
- `process_scalars.py` — builds the flag from three integer scalars

The challenge description is full of hints:
- "Glen's Enigmatic Module" = **GEM** = Gaussian Elimination Method, the classic algorithm for computing **determinants**
- "ritual of the gate" = the determinant operation (the "gate" scalar of a matrix)
- "grid-formed relics" = 3x3 kernel matrices
- "chromatic layers" = RGB channels

**Step 1:** Run the kernel recovery script:
```bash
python3 retrieve_kernel.py flower flower_processed
```

This outputs three 3x3 integer kernels, one per channel.

**Step 2:** Compute the determinant of each kernel:
- Red: det = 1
- Green: det = 40
- Blue: det = 35

**Step 3:** Pass to the flag script:
```bash
python3 process_scalars.py 1 40 35
# apoorvctf{1_40_35}
```

## Key Takeaways
- Challenge descriptions in CTFs are rarely fluff — parse every word for algorithmic hints
- "GEM" is a well-known abbreviation for Gaussian Elimination Method (determinant computation)
- Convolution kernel recovery via least-squares is a standard linear algebra technique
