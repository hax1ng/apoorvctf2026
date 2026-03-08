# Riddler

**Category:** Crypto | **Difficulty:** Easy | **Flag:** `apoorvctf{3ncrypt1ng_w1th_RSA_c4n_b3_4_d4ng3r0us_cl1ff_83}`

## Overview
RSA encryption with e=3 where the message is small enough that m^3 < N.

## Solution
The challenge provides standard RSA parameters: N (2048-bit), e=3, and ciphertext c. The ciphertext is significantly smaller than N, which is the telltale sign that no modular reduction occurred during encryption.

Since `c = m^3 mod N` but `m^3 < N`, we have `c = m^3` exactly. Taking the integer cube root of c directly recovers the plaintext.

```python
root, exact = gmpy2.iroot(c, 3)  # exact = True
```

See `solve.py` for the full exploit.

## Key Takeaways
- When RSA uses a small public exponent (e=3), always check if the message is small enough that m^e < N.
- If the direct eth root doesn't work, try `c + k*N` for small values of k (Hastad-style).
