#!/usr/bin/env python3
"""
Forge CTF Challenge Solver

The binary performs Gaussian elimination over GF(2^8) on a 56x56 matrix
(augmented with a 56-byte column vector). The solution vector is the flag.

Matrix data: 0x402080 (56x56 = 3136 bytes)
Augmentation column: 0x402040 (56 bytes)
GF(2^8) with AES polynomial x^8+x^4+x^3+x+1 (0x11b)
"""

# GF(2^8) arithmetic with AES polynomial
def gf_mul(a, b):
    """Multiply two elements in GF(2^8) with polynomial 0x11b"""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xff
        if hi:
            a ^= 0x1b
        b >>= 1
    return p

def gf_inv(a):
    """Find multiplicative inverse in GF(2^8)"""
    if a == 0:
        return 0
    # Brute force - fine for 256 elements
    for x in range(1, 256):
        if gf_mul(a, x) == 1:
            return x
    return 0

# Read matrix data from binary
import struct

with open("/home/kali/CTF/aproovctf2026/rev/Forge/forge", "rb") as f:
    data = f.read()

# Find offsets in the file for the virtual addresses
# The binary is PIE but loaded at known addresses for data section
# data_402080 and data_402040 - need to find file offsets

# Let's search for the known bytes at 0x402040
aug_pattern = bytes([0xcb, 0xc0, 0x47, 0x1c, 0x11, 0x61, 0xd7, 0x07])
aug_offset = data.find(aug_pattern)
print(f"Augmentation column found at file offset: 0x{aug_offset:x}")

mat_pattern = bytes([0x69, 0xb7, 0xe3, 0x55, 0xb3, 0x2b, 0x99, 0x61])
mat_offset = data.find(mat_pattern)
print(f"Matrix data found at file offset: 0x{mat_offset:x}")

# Extract the data
N = 56  # 0x38

# Augmentation column (56 bytes)
aug = list(data[aug_offset:aug_offset + N])
print(f"Augmentation: {aug[:8]}...")

# Matrix (56x56)
mat_data = data[mat_offset:mat_offset + N*N]
matrix = []
for i in range(N):
    row = list(mat_data[i*N:(i+1)*N])
    matrix.append(row)

print(f"Matrix size: {len(matrix)}x{len(matrix[0])}")

# Now, reconstruct the augmented matrix as the binary does
# The binary loads data_402080 as 56x56 matrix into rows of stride 0x39 (57)
# with data_402040 as the 57th column (augmentation)
# But looking at the decompilation more carefully:
#
# The loading loop copies 0x38 bytes from data_402080 per row
# and 1 byte from data_402040 per row
# Each row is 0x39 bytes: [56 bytes from matrix][1 byte from augmentation]

# Build augmented matrix (56 rows x 57 cols)
aug_matrix = []
for i in range(N):
    row = list(matrix[i]) + [aug[i]]
    aug_matrix.append(row)

# Gaussian elimination over GF(2^8)
print("\nPerforming Gaussian elimination over GF(2^8)...")

for col in range(N):
    # Find pivot
    pivot_row = -1
    for row in range(col, N):
        if aug_matrix[row][col] != 0:
            pivot_row = row
            break

    if pivot_row == -1:
        print(f"No pivot found for column {col}!")
        continue

    # Swap rows if needed
    if pivot_row != col:
        aug_matrix[col], aug_matrix[pivot_row] = aug_matrix[pivot_row], aug_matrix[col]

    # Scale pivot row
    inv = gf_inv(aug_matrix[col][col])
    for j in range(N + 1):
        aug_matrix[col][j] = gf_mul(aug_matrix[col][j], inv)

    # Eliminate column in all other rows
    for row in range(N):
        if row == col:
            continue
        factor = aug_matrix[row][col]
        if factor == 0:
            continue
        for j in range(N + 1):
            aug_matrix[row][j] ^= gf_mul(factor, aug_matrix[col][j])

# Extract solution (last column)
solution = bytes([aug_matrix[i][N] for i in range(N)])
print(f"\nSolution ({len(solution)} bytes):")
print(f"  Hex: {solution.hex()}")
print(f"  ASCII: {solution}")

# Check if it looks like a flag
try:
    flag = solution.decode('ascii', errors='replace')
    print(f"\nFlag: {flag}")
except:
    print("\nNot pure ASCII, trying to find flag pattern...")

# Also try the extraction pattern from the binary
# The binary extracts from the state differently - let me check
# The extraction at 0x401489 reads diagonals from the solved state
