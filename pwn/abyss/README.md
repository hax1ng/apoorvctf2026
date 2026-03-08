# Abyss

**Category:** pwn | **Difficulty:** Medium-Hard | **Flag:** `apoorvctf{th1s_4by55_truly_d03s_5t4r3_b4ck}`

## Overview
A custom command-line service with an ocean-depth theme that manages "dive" and "leviathan" (beacon) objects using a slab allocator. It uses io_uring for async I/O and has a benthic thread that can open and read `/flag.txt` when given a properly crafted io_uring SQE.

## Solution

### Recon
The binary (`abyss`) is a PIE ELF64 with full protections (RELRO, canary, NX, PIE, FORTIFY). It implements a command protocol: DIVE, DESCEND, WRITE, POP, FLUSH, STATUS, BEACON, ABYSS, ECHO, HELP, QUIT.

Key architecture:
- **dive_slab** (16 entries, 0x60 bytes each): Allocates "dive" objects
- **levi_slab** (16 entries): Allocates "leviathan/beacon" objects
- **g_dive_reg** (16 slots): Registry of dive pointers
- **g_levi_reg** (24 slots): Registry of leviathan pointers
- Slab freelists are XOR-encoded with a random `g_slab_secret`
- Three threads: main (parser), mesopelagic (cleanup), benthic (io_uring worker)

### The Vulnerability: Use-After-Free via FLUSH

The `FLUSH` command tells the mesopelagic thread to walk `g_request_stack` and free all dive objects back to `dive_slab`. However, it does NOT clear the corresponding `g_dive_reg` entries. This creates a classic **use-after-free**: the freed object's memory can be reused (by a BEACON allocation from dive_slab), while `g_dive_reg` still holds a pointer to it.

### The ABYSS + BEACON Mechanism

When `ABYSS <levi_id>` is called, the benthic thread takes the leviathan's note data (64 bytes at object+8) and submits it directly as an io_uring SQE. If the SQE opcode is `IORING_OP_OPENAT` (0x12), benthic automatically follows up by reading from the opened fd into a flag buffer and sending the contents back.

BEACONs are normally allocated from `levi_slab`, but when it's exhausted, they fall back to `dive_slab`. BEACON allocation zeroes the note area, so we can't pre-fill data before allocation.

### Exploitation Strategy

1. **Exhaust dive_slab**: Allocate 16 dives (fills all slots)
2. **Leak PIE**: Use `STATUS 0` to get dive 0's address, calculate PIE base
3. **Exhaust levi_slab**: Allocate 16 beacons (BEACON 0-15)
4. **FLUSH**: Free all dives back to dive_slab (UAF — g_dive_reg preserved)
5. **BEACON 16**: Allocates from dive_slab (levi exhausted), gets dive 0's memory
6. **DESCEND 0**: Write a crafted OPENAT SQE into the shared memory via the stale g_dive_reg[0] reference
7. **ABYSS 16**: Benthic submits our SQE, opens `/flag.txt`, reads and returns the flag

### The SQE Payload

```
opcode  = 0x12 (IORING_OP_OPENAT)
fd      = -100 (AT_FDCWD)
addr    = PIE_BASE + 0x6010 (address of "/flag.txt" string in .data)
flags   = O_RDONLY (0)
```

See `solve.py` for the full exploit code.

## Key Takeaways
- FLUSH operations that free resources without clearing all references create UAF opportunities
- Custom slab allocators with XOR-encoded freelists add complexity but don't prevent logical UAF bugs
- io_uring SQE injection is a powerful primitive when you can control the SQE bytes
- Exhausting both slab pools forces cross-pool allocation, enabling type confusion between dive and leviathan objects
