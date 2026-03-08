# Golden Experience

**Category:** Reversing | **Difficulty:** Easy | **Flag:** `apoorvctf{N0_M0R3_R3QU13M_1N_TH15_3XP3R13NC3}`

## Overview
A stripped Rust binary that constructs the flag via XOR, briefly prints it, then immediately zeroes the buffer — themed after JoJo's Gold Experience Requiem.

## Solution
The binary `requiem` is a Rust ELF that:
1. Prints "loading flag"
2. Allocates a 45-byte buffer
3. XORs 45 hardcoded bytes (at `0x4484f4`) with key `0x5a` to build the flag
4. Prints the flag ("printing flag.....")
5. Immediately zeroes out the buffer (the "Requiem" — reverting to zero)

Static analysis with Binary Ninja reveals the XOR loop and the hardcoded data. Extracting the bytes and XORing with `0x5a` gives the flag directly:

```python
data = bytes([0x3b,0x2a,0x35,0x35,0x28,0x2c,0x39,0x2e,0x3c,0x21,
              0x14,0x6a,0x05,0x17,0x6a,0x08,0x69,0x05,0x08,0x69,
              0x0b,0x0f,0x6b,0x69,0x17,0x05,0x6b,0x14,0x05,0x0e,
              0x12,0x6b,0x6f,0x05,0x69,0x02,0x0a,0x69,0x08,0x6b,
              0x69,0x14,0x19,0x69,0x27])
print(bytes([b ^ 0x5a for b in data]).decode())
```

## Key Takeaways
- Rust binaries are verbose but the core logic is usually compact — find `main` and trace the actual program function.
- Single-byte XOR is trivially reversible via static analysis — no need to run the binary.
- When a challenge hints at destruction/erasure, static analysis bypasses runtime tricks entirely.
