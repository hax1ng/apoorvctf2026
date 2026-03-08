#!/usr/bin/env python3
"""Solve Shake It To The Max - hardware encryption challenge"""
import csv

# Parse the CSV truth table
rows = []
with open('encrypto.csv') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        rows.append([int(x, 16) if x != '_' else None for x in row])

msg = 'SHAKEITTOTHEMAX'

# The CSV contains 8 columns (o0-o7) representing different rounding variants
# of the same multiplication: input * 8/3.
# Column 5 gives ceil(input * 8/3) = (input * 8 + 2) // 3.
# The hint "MIN TO THE MAX" + Quine-McCluskey points to the minterms of
# the boolean functions implementing this ceiling division in hardware.
encrypted = ''.join(format(rows[ord(ch)][5], '02x') for ch in msg)

# Equivalent closed-form: output = ceil(input * 8/3)
assert encrypted == ''.join(f'{(ord(ch)*8+2)//3:02x}' for ch in msg)

flag = f'apoorvctf{{{encrypted}}}'
print(flag)
