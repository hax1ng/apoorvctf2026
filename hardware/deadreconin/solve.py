#!/usr/bin/env python3
"""Solve script for deaDr3con'in - Apoorvctf 2026 Hardware Challenge"""

import struct, re, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

with open('controller_fw.bin', 'rb') as f:
    data = f.read()

# Firmware structure:
# 0x0000-0x003F: ARM Cortex-M vector table
# 0x0040-0x03FF: NOP padding (Thumb MOV R8,R8)
# 0x0400-0x0BFF: Strings section
# 0x0C00-0x0C21: Config struct (magic, baud, axis limits, cal_reserved)
# 0x0C22-0x0FFF: Padding
# 0x1000-0x100F: Job buffer header "JBUFHDR5SEG4" + 4-byte total length
# 0x1010-0x31A2: Encrypted job data (4 segments)
# 0x31A3-0x4FFF: 0xFF padding
# 0x5000-0x5009: "AXIOM_END"

# XOR key (8 bytes, derived via frequency analysis on G-code character set)
key = bytes([0x08, 0xf1, 0x4c, 0x3b, 0xa7, 0x2e, 0x91, 0xc4])

def decrypt(enc_data, key_offset=0):
    dec = bytearray(len(enc_data))
    for i in range(len(enc_data)):
        dec[i] = enc_data[i] ^ key[(i + key_offset) % 8]
    return dec.decode('latin-1')

# Segment layout (fragmented, "JOB BUFFER FRAGMENTED"):
# Main payload at 0x1010, 3986 bytes: seg 4/4, key offset 0
# Packet at 0x1FA3: [4B len=1580][1B seg_id=0] -> seg 1/4, key offset 1
# Packet at 0x25D4: [4B len=2767][1B seg_id=2] -> seg 3/4, key offset 1
# Packet at 0x30A8: [4B len=246][1B seg_id=1]  -> seg 2/4, key offset 1

seg1 = decrypt(data[0x1FA8:0x1FA8+1580], 1)  # seg:1/4 - letter 'f'
seg2 = decrypt(data[0x30AD:0x30AD+246], 1)    # seg:2/4 - apostrophe "'"
seg3 = decrypt(data[0x25D9:0x25D9+2767], 1)   # seg:3/4 - letter 'G'
seg4 = decrypt(data[0x1010:0x1010+3986], 0)    # seg:4/4 - letter 'S'

all_gcode = seg1 + '\n' + seg2 + '\n' + seg3 + '\n' + seg4

# Parse G-code and extract cutting paths
def parse_gcode(gcode_text):
    lines = gcode_text.strip().split('\n')
    x, y, z = 0.0, 0.0, 5.0
    paths = []
    current = []
    for line in lines:
        line = line.strip()
        if line.startswith('(') or line == '%' or line.startswith('M') or line.startswith('G21'):
            continue
        m = re.match(r'G(\d+)', line)
        if not m:
            continue
        cmd = int(m.group(1))
        params = {}
        for p in re.finditer(r'([XYZIJF])([-\d.]+)', line):
            params[p.group(1)] = float(p.group(2))
        nx, ny, nz = params.get('X', x), params.get('Y', y), params.get('Z', z)
        if cmd == 0:
            if current: paths.append(current); current = []
            x, y, z = nx, ny, nz
        elif cmd == 1:
            if nz < 0:
                if not current: current.append((x, y))
                current.append((nx, ny))
            elif current: paths.append(current); current = []
            x, y, z = nx, ny, nz
        elif cmd in (2, 3):
            cx, cy = x + params.get('I', 0), y + params.get('J', 0)
            r = math.sqrt((x-cx)**2 + (y-cy)**2)
            sa = math.atan2(y-cy, x-cx)
            ea = math.atan2(ny-cy, nx-cx)
            if cmd == 2 and ea >= sa: ea -= 2*math.pi
            if cmd == 3 and ea <= sa: ea += 2*math.pi
            n = max(30, int(abs(ea-sa)*r/0.3))
            if nz < 0:
                if not current: current.append((x, y))
                for t in np.linspace(sa, ea, n)[1:]:
                    current.append((cx+r*math.cos(t), cy+r*math.sin(t)))
            elif current: paths.append(current); current = []
            x, y, z = nx, ny, nz
    if current: paths.append(current)
    return paths

paths = parse_gcode(all_gcode)

# Rotate text to horizontal (~38.7 degrees)
angle = -math.atan2(80, 100)
cos_a, sin_a = math.cos(angle), math.sin(angle)
cx_r, cy_r = 90, 90
def rotate(x, y):
    dx, dy = x-cx_r, y-cy_r
    return dx*cos_a - dy*sin_a + cx_r, dx*sin_a + dy*cos_a + cy_r

fig, ax = plt.subplots(1, 1, figsize=(24, 10))
for path in paths:
    pts = [rotate(p[0], p[1]) for p in path]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], 'k-', linewidth=2.5)
ax.set_aspect('equal')
ax.set_title("CNC Engraving: f'GS")
ax.grid(True, alpha=0.3)
fig.savefig('engraving_flag.png', dpi=150, bbox_inches='tight')
plt.close()

print("Flag: apoorvctf{f'GS}")
