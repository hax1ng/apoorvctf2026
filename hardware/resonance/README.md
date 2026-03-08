# Resonance Lock

**Category:** Hardware | **Difficulty:** Medium | **Flag:** `apoorvctf{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}`

## Overview
TCP service simulating a UART baud-rate oscillator that requires calibration before accepting 512-bit multiplication operands to release a flag.

## Solution
The challenge describes an elaborate UART calibration protocol, but the actual server is much simpler:

1. **Connect** to `chals4.apoorvctf.xyz:1337` with `TCP_NODELAY`
2. **Send byte `0xCA`** to enter calibration mode (do NOT send the text "CALIBRATE" — any unexpected bytes blow the HSM tamper fuse)
3. **Send 5 calibration bursts** of 64 bytes of `0x55` each. The server responds with `EXEC_TIME:268380` for each burst and prints `LOCKED` after the 5th
4. **Send multiplication payload**: `0xAA` + 64-byte A + 64-byte B (any valid 512-bit big-endian values work)
5. Server responds with the flag

The precise baud timing described in the challenge is not actually enforced — sending all 64 bytes at once works fine. The key insight is avoiding the tamper fuse by not sending garbage or text commands.

See `solve.py` for the full exploit.

## Key Takeaways
- Don't over-engineer based on challenge descriptions — test the simplest approach first
- The "CALIBRATE" was a description of the mode, not something to send as text
- HSM tamper fuse is session-permanent — reconnect if you trigger it
