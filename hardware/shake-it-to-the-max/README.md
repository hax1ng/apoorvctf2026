# Shake It To The Max

**Category:** Hardware | **Difficulty:** Medium | **Flag:** `apoorvctf{dec0aec8b8c3e0e0d3e0c0b8ceaeeb}`

## Overview
Given a circuit diagram of an "ENCRYPTA" chip and a CSV truth table, encrypt the message "SHAKEITTOTHEMAX" to find the drone swarm shutdown command.

## Solution
The challenge provides two files:
- **encrypto.png** — circuit diagram showing an 8-bit input/output chip with an AND gate labeled "MAX" providing feedback
- **encrypto.csv** — table with 107 rows (row index = input value 0-106) and 8 columns (o0-o7)

The hint mentions "Quine-McCluskey tables" and "MIN TO THE MAX under an AND logic gate," pointing toward boolean function minimization of a hardware multiplier.

Analysis of the 8 columns reveals they all implement variants of the same operation: **multiplication by 8/3** with different rounding behaviors. Each column represents a different truncation/rounding of the division:

| Column | Formula | Description |
|--------|---------|-------------|
| o4 | `(8*i + 5) // 3` | Highest rounding (MAX) |
| o5 | `(8*i + 2) // 3` | Ceiling division |
| o7 | `(8*i + 4) // 3` | Near-ceiling |
| o6 | `(8*i - 1) // 3` | Floor division |

Column 5 gives the **ceiling division**: `ceil(input × 8/3) = (input × 8 + 2) // 3`.

The encryption is simply: for each character in "SHAKEITTOTHEMAX", compute `ceil(ASCII_value × 8/3)` and express as 2-digit lowercase hex.

```python
msg = 'SHAKEITTOTHEMAX'
encrypted = ''.join(f'{(ord(ch)*8+2)//3:02x}' for ch in msg)
print(f'apoorvctf{{{encrypted}}}')
```

## Key Takeaways
- Hardware truth tables can encode multiple rounding variants of the same arithmetic operation — identifying the underlying formula (×8/3) was key
- The CSV columns aren't independent functions but rather different truncation behaviors of integer division in a hardware multiplier
- The hint "MIN TO THE MAX" refers to the Quine-McCluskey minimization of boolean functions implementing the ceiling division circuit
