# Tick Tock

**Category:** Crypto | **Difficulty:** Medium | **Flag:** `apoorvctf{con5t4nt_tim3_or_di3}`

## Overview
A password verification service that checks digits one at a time with an early-return on mismatch, leaking the password through timing side-channel.

## Solution
The server checks each digit of the password sequentially, sleeping ~0.8 seconds per correct digit before comparing the next one. An incorrect digit returns immediately. This classic timing attack lets us recover the password digit by digit.

1. For each position, try all 10 digits (0-9) and measure response time
2. The digit that takes ~0.8s longer than the others is correct
3. Append that digit and move to the next position
4. When the server responds with "Correct!", we have the full password

The signal was extremely clear (~800ms per correct digit), so even 3 rounds of measurement per digit sufficed. The main challenge was keeping the connection alive — reconnecting per round solved server timeouts.

Password: `934780189098` (12 digits)

Reference `solve.py` for the full exploit code.

## Key Takeaways
- Timing side-channels with ~800ms granularity are trivially exploitable over the network
- The flag hints at the fix: use **constant-time comparison** (`hmac.compare_digest` in Python, `crypto.timingSafeEqual` in Node.js)
- Reconnecting between rounds avoids server idle timeouts on longer passwords
- Median is more robust than mean for timing measurements over network
