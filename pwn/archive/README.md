# Archive (Havok)

**Category:** Pwn | **Difficulty:** Medium-Hard | **Flag:** `apoorvctf{c0sm1c_b4rr13rs_br0k3n_4nd_h4v0k_s3cur3d}`

## Overview
A PIE binary with seccomp sandbox presents four "cosmic rings" (barriers) that must be broken to read `/flag.txt`.

## Solution

**Ring 1 — OOB Read (Leak libc + PIE):** `calibrate_rings()` reads an index as int32, validates `>=0`, then casts to int16_t and validates `<=3`. Sending 65534 (int16=-2) and 65535 (int16=-1) reads past the ring array into puts@GOT and &main, leaking libc and PIE base addresses.

**Ring 2 — Label Input:** Just send any string; no exploit needed here.

**Ring 3 — Plasma Signature (ROP payload):** `read_plasma_signature()` reads 256 bytes into BSS at elf+0x4060. `validate_plasma()` scans for `0x0f 0x05` bytes (syscall opcode) — if ASLR places gadgets such that they contain these bytes, retry. The ROP chain uses raw syscalls for open-read-write:

```
open("/flag.txt", 0)         → rax = fd
xchg rdi, rax; cld; ret      → rdi = fd (dynamic, not hardcoded!)
pop rsi; ret                  → rsi = buffer
pop rdx; xor eax,eax; ret    → rdx = size, eax = 0 = SYS_read
syscall; ret                  → read(fd, buf, 0x80)
pop rdi; ret → 1              → stdout
pop rsi; ret → buf            → buffer
pop rdx; xor eax,eax; ret    → size
pop rax; ret → 1              → SYS_write
syscall; ret                  → write(1, buf, 0x80)
```

The `/flag.txt\0` string is placed at offset 0xe0 within the payload.

**Ring 4 — Stack Overflow + Pivot:** `inject_plasma()` reads 0x30 bytes into a 0x20 buffer with no canary. Overflow sets saved RBP = plasma_sig_addr (BSS) and return address = `leave; ret` gadget. The `leave` instruction does `mov rsp, rbp; pop rbp`, pivoting the stack to BSS where the ROP chain waits.

**Critical detail:** The `xchg rdi, rax` gadget (libc+0x181fe1) is essential because Docker/socat environments have extra file descriptors open, so `open()` doesn't return fd=3. Using `xchg` dynamically passes the actual fd to `read()`.

See `solve.py` for the full exploit. Retry loop handles ASLR randomization that might place `0x0f 0x05` in the payload.

## Key Takeaways
- Integer truncation (int32→int16_t) bypasses bounds checks when only the truncated value is validated
- In containerized/socat environments, never hardcode file descriptor numbers — use `xchg rdi, rax` or similar to capture `open()`'s return value
- `pop rdx; xor eax, eax; ret` is a powerful dual-purpose gadget: sets rdx AND eax=0 (SYS_read)
- When seccomp blocks execve, raw syscall ORW is the standard approach
- Payload byte filtering (0x0f 0x05 scan) can be bypassed via ASLR retry since gadget addresses change each run
