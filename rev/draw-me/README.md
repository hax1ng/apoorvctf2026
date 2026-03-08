# Draw Me

**Category:** Reversing | **Difficulty:** Medium | **Flag:** `apoorvctf{GL5L_15_7UR1NG_C0MPL373}`

## Overview
A WebGL2 shader implements a custom VM on a 256x256 texture. A PNG file contains the bytecode. The challenge: "nothing renders" because the GPU's one-write-per-frame limitation loses most pixel data.

## Solution

### Understanding the VM
The GLSL fragment shader is a tiny CPU running on the GPU. The 256x256 texture is divided into:
- **Row 0**: Registers (pixel 0 = instruction pointer, pixels 1-32 = general purpose)
- **Rows 1-127**: Program memory (RGBA = opcode, arg1, arg2, arg3)
- **Rows 128-255**: VRAM (display output)

10 opcodes: NOP, SET, ADD, SUB, XOR, JMP, JNZ, VRAM-write, STORE, LOAD. 16 steps per frame.

### Self-Modifying Code
The program has two phases:

1. **Decryption** (4080 instructions): XORs constants (90 or 165) with key=90 to produce 0 or 255, then STORE patches 510 "SET r4" instructions in the drawing code.

2. **Drawing** (2040 instructions): Executes patched code — each pixel is SET r4=color, SET r2=x, SET r3=y, VRAM-write.

### Why Nothing Renders
The GPU runs all pixels in parallel each frame, but the shader only tracks ONE vram write target. With 4 VRAM writes per 16-step frame, only the last survives — losing 75% of pixels. Similarly, half the STORE patches are lost during decryption.

### The Solve
Instead of running the GPU shader, emulate the VM sequentially in Python — apply ALL decryption patches immediately, then execute ALL VRAM writes. This recovers the full intended image.

```python
# Key: sequential emulation applies all writes, not just last-per-frame
# See solve.py for full implementation
```

The output renders pixel-font text: `APOORVCTF{GL5L_15_7UR1NG_C0MPL373}`

Leetspeak decode: **GLSL IS TURING COMPLETE** (S→5, I→1, T→7, O→0, E→3)

## Key Takeaways
- GLSL shaders can implement Turing-complete VMs — the flag is literally the message
- Self-modifying code: STORE opcode patches program memory before drawing
- GPU parallelism causes write conflicts — static/sequential analysis recovers the full output
- In 3x5 pixel fonts, O and 0 are identical — leetspeak context (O→0) resolves the ambiguity
