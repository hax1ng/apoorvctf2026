# The Riddler's Cipher Delight 2

**Category:** Crypto | **Difficulty:** Hard (500 pts) | **Flag:** `apoorvctf{0x0xh3_who_sk1ps_n0+steps_l4ghs}`

## Overview
Multi-step crypto chain challenge requiring RSA Wiener's attack, Brainfuck/Malbolge interpretation, minisign signature analysis, and RSA cube root attacks.

## Solution

### Step 1: Wiener's Attack
`chall.py` provides RSA with a small 256-bit private key `d`. Using continued fraction expansion of `e/N`, we recover `d` and decrypt the ciphertext to get `rentry.co/actf1`.

### Step 2: Brainfuck
The actf1 page contains Brainfuck code that outputs a base64 string decoding to "this is a dead end.. or is it ?" — a hint to keep looking.

### Step 3: Malbolge
Via actf2 → actf3, we find Malbolge code that outputs a minisign verification command with a public key: `RWQ454fqCYMUjvs8f7Cen3i8dv3xwporJuYHAd+yLjyMAQO2HEcrj2zU`

### Step 4: Finding the Right Signature
Searching rentry pages for minisign signatures matching the public key, we find **actf100** (not actf27, which was a decoy pointing to thiccattraction with broken RSA values). actf100's signature points to `rentry.co/actual_msg`.

### Step 5: RSA Cube Root Chain
`actual_msg` contains an RSA challenge with e=3. Since the ciphertext c is small enough that m^3 < N, we take the exact cube root: `gmpy2.iroot(c, 3)` → `rentry.co/areyoufinallyhere`.

That page has one more RSA with e=3. Same cube root attack yields the flag.

```python
import gmpy2
from Crypto.Util.number import long_to_bytes
c = 151257482287264675048693086395951517096037073890938926157024279458804334671781029202065147368120659639119210196959107547394828892481682960056998640516788115100676808516910681926773417384817402924724757047240437835434369545296563335528699943734236716634866269787920798041627639490695656674748372561030757
root, exact = gmpy2.iroot(c, 3)
print(long_to_bytes(int(root)).decode())
# apoorvctf{0x0xh3_who_sk1ps_n0+steps_l4ghs}
```

## Key Takeaways
- The thiccattraction page was a deliberate red herring with mathematically invalid RSA parameters (N divisible by 7/241 making e incompatible with phi)
- When multiple rentry pages exist, verify which one has the correct data — don't assume the first match is right
- Small public exponent e=3 with small plaintext → cube root attack (no factoring needed)
- The flag text itself hints at the solve: "he who skips no steps laughs" — you need patience through the full chain
