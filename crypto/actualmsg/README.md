# Actual Message

**Category:** Crypto | **Difficulty:** Hard | **Flag:** `apoorvctf{_h3h3_ma0r_RSA_f4ilur33_modes_67}`

## Overview
Multi-layered RSA challenge spread across rentry.co pages, with decoy flags, esolang programs, and XOR-obfuscated ciphertext. Finding the real chain requires enumerating hidden actf pages.

## Solution

### Step 1: Initial RSA (e=3)
The challenge gives `new-new_enc.py` with RSA parameters where e=3. Direct cube root of c gives `rentry.co/areyoufinallyhere` — but this leads to a **decoy flag**.

### Step 2: Find the real chain
The challenge hints (actf2: "try different variants of actfXYZ") tell you to enumerate `rentry.co/actf1` through `actf150`. Most are decoys, but **actf88** points to `rentry.co/someunrealatedbsname` with another RSA e=3. Cube root gives `https://rentry.co/lemonyrick67691`.

### Step 3: XOR-obfuscated RSA
`lemonyrick67691` contains an RSA script that XOR-obfuscates the output:
```python
print("N = ", (N^k^c))     # k = 512-bit prime
print("e = ", (e^k^l))     # l = 10-bit prime, e = 65537
print("c = ", (c^e^l))
```

Since `e_out = 65537 ^ k ^ l`, we compute `k ^ l = e_out ^ 65537`. Then brute-force `l` over all 75 ten-bit primes until `k = (k^l) ^ l` is a 512-bit prime. This recovers the real N, e=65537, and c.

The recovered N turns out to be the **same N from `enccc.py`** (a separate Wiener's attack challenge). Using the known `e*d - 1` from Wiener's attack, we factor N via the standard randomized algorithm and decrypt to get `rentry.co/nakedcitrus21`.

### Step 4: Final flag
`nakedcitrus21` has one more RSA e=3 challenge. The cube root doesn't work directly (m^3 > N), but trying `c + k*N` with k=41 gives the flag.

See `solve.py` for the full exploit.

## Key Takeaways
- Always enumerate when a challenge hints at hidden pages — actf88 was the critical link
- Decoy flags and rickrolls are common in multi-step CTF challenges; verify your path
- RSA modulus reuse across challenges is a powerful vulnerability — factoring one breaks all
- XOR "encryption" with a small brute-forceable parameter is trivially reversible
- The Wiener's attack result from a separate challenge (enccc.py) was needed to complete this one — cross-challenge dependencies!
