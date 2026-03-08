# Engraver's Fault

**Category:** Forensics | **Difficulty:** Hard (500pts) | **Flag:** `apoorvctf{1d3nt1ty_cr1515_f0r_1m4g35_h4h4h4}`

## Overview
A gallery of 352 JPEG images (249 numbered 104-352 + 103 timestamped IMG files) hides a binary message in the DCT coefficient distribution of the numbered images.

## Solution

### 1. Identify the Covert Channel
The challenge name "engraver's fault" hints at invisible modifications left by a steganographic tool. In JPEG, this means DCT (Discrete Cosine Transform) coefficient manipulation — similar to F5 steganography, which decrements coefficient magnitudes.

### 2. Detect Modified Images via DCT Analysis
Using `jpegio` to read raw DCT coefficients, we analyze the ratio of ±1 to ±2 AC coefficients in the luminance channel. Natural JPEGs have a ratio of 0.25-0.45. F5-modified images have dramatically reduced ratios (< 0.10) because ±1 coefficients get decremented to 0.

The distribution is clearly bimodal with a gap from 0.1428 to 0.2150:
- **Modified images** (ratio < 0.15): 122 numbered files
- **Clean images** (ratio >= 0.15): 127 numbered + all 103 IMG files

### 3. Handle the Sparse Image Edge Case (File 336)
File 336 appeared "clean" by the ±1/±2 ratio (0.2263) but was actually modified. The image is unusually sparse (80% zero coefficients), which artificially inflates the ratio.

The ±2/±3 ratio exposed the truth:
- File 336: r23 = 2.15 (matches modified-sparse files)
- Truly clean files: r23 = 2.96+
- Combined rule: modified if `r12 < 0.15` OR `(r12 < 0.25 AND r23 < 2.5)`

### 4. Extract the Binary Message
Each numbered file from 105 to 352 encodes one bit:
- **Clean** → `1`, **Modified** → `0`

248 bits = 31 bytes of ASCII:
```
nt1ty_cr1515_f0r_1m4g35_h4h4h4}
```

The decoded suffix `nt1ty` is clearly the tail of "identity". Prepend `1d3` (leetspeak "ide") to complete it.

Leetspeak: "identity crisis for images hahaha"

### 5. Construct the Flag
```
apoorvctf{1d3nt1ty_cr1515_f0r_1m4g35_h4h4h4}
```

## Key Takeaways
- The ±1/±2 AC coefficient ratio is a powerful F5-stego detector, but **sparse images can give false negatives** — cross-check with the ±2/±3 ratio.
- A gallery of images can encode a binary message using 1 bit per image (modified vs clean DCT distribution).
- Always verify borderline classifications with secondary metrics, especially for images with unusual sparsity.
