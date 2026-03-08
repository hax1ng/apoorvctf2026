# House of Wade

**Category:** Pwn | **Difficulty:** Medium | **Flag:** `apoorvctf{w4d3_4ppr0v3s_0f_y0ur_h34p_sk1llz}`

## Overview
Heap menu challenge with a UAF vulnerability — poison tcache to overwrite a magic value and get the flag.

## Solution

The binary is a chimichanga shop with 6 menu options. At startup it does `chimichanga_count = malloc(0x28)` and memsets it to zero. The win function `did_i_pass` checks if `*chimichanga_count == 0xcafebabe` and prints the flag.

The `cancel_order` function frees a chunk but never NULLs the pointer ("The pointer remains, like a bad memory"), giving us a classic **Use-After-Free**. `inspect_order` reads from freed chunks (UAF read) and `modify_order` writes to them (UAF write).

Since both orders and `chimichanga_count` use `malloc(0x28)` (same 0x30 tcache bin), we can use **tcache poisoning** to redirect an allocation to the chimichanga chunk:

1. Allocate two orders (slots 0, 1)
2. Free order 0, then UAF-read it to leak the mangled tcache fd pointer → recover heap base
3. Free order 1 → tcache chain: order1 → order0
4. UAF-write order 1's fd to point to chimichanga's chunk (accounting for glibc 2.35 safe-linking: `mangled = target ^ (pos >> 12)`)
5. Allocate twice: first pops order1, second pops the chimichanga chunk into a new slot
6. Modify the new slot to write `0xcafebabe`
7. Claim prize → flag

See `solve.py` for the full exploit.

## Key Takeaways
- glibc 2.35 tcache uses safe-linking — must XOR pointers with `chunk_addr >> 12`
- UAF without NULL-ing pointers is a textbook heap exploitation primitive
- Same-size allocations land in the same tcache bin, making poisoning straightforward
