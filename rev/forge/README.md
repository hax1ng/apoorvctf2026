# Forge

**Category:** Reversing | **Difficulty:** Medium-Hard | **Flag:** `apoorvctf{Y0u_4ctually_brOught_Y0ur_owN_Firmw4re????!!!}`

## Overview

A stripped 64-bit ELF binary that performs Gaussian elimination over GF(2^8) on a hardcoded 56x56 matrix to produce the flag, then encrypts it with AES-256-GCM before outputting.

## Solution

### Reconnaissance

The binary imports OpenSSL crypto functions (AES-256-GCM, SHA256) and anti-debugging primitives (ptrace, prctl, sigprocmask). It mmaps two regions: one for shellcode execution (0x20000000) and one for shared data (0x40000000).

### Core Logic

The binary's main computation:

1. **Loads a 56x56 byte matrix** from `0x402080` and a 56-byte augmentation column from `0x402040`
2. **Performs Gaussian elimination over GF(2^8)** using an AES-polynomial multiplication table at `0x402cc0` (polynomial `x^8+x^4+x^3+x+1 = 0x11b`)
3. **Extracts the solution vector** (56 bytes) — this is the flag
4. The flag is then AES-256-GCM encrypted with a time-derived key and stored in shared memory
5. A child process (loaded from external shellcode file `payload>bin`) is expected to decrypt it
6. Parent verifies the child's output via SHA256 comparison and prints the flag

### Solving

Since the flag is the solution to the linear system `Ax = b` over GF(2^8), we can solve it directly without running the binary:

1. Extract the 56x56 matrix `A` and 56-byte vector `b` from the binary
2. Implement GF(2^8) arithmetic (multiplication, inverse) with the AES polynomial
3. Perform Gaussian elimination on the augmented matrix `[A|b]`
4. Read off the solution vector — it's the flag in ASCII

See `solve.py` for the full implementation.

## Key Takeaways

- Recognizing the GF(2^8) multiplication table (256x256 lookup table with AES polynomial) was critical
- The stride-0x39 row layout (56 data bytes + 1 augmentation byte) confirmed this was an augmented matrix for a linear system
- The anti-debugging, shellcode loading, and AES-GCM encryption were all distractions — the flag is recoverable purely from static data embedded in the binary
