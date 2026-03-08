#!/usr/bin/env python3
"""
GLSL VM emulator - static analysis approach.

The program has two phases:
1. Decryption (251,8 to 235,24): XORs values and STOREs them into program memory
2. Drawing (2,1 to 250,8): Writes pixels to VRAM using opcode 7

We can statically compute the STORE effects, apply them, then trace the drawing.
"""
from PIL import Image
import numpy as np

img = Image.open('program.png').convert('RGBA')
state = np.array(img, dtype=np.int32).copy()

# Phase 1: Trace the decryption code statically
# reg[1] = 90 (set at (0,1))
# Then code at (251,8) onward does repeated:
#   SET r8 = val
#   XOR r4 = r8 ^ r1  (i.e., val ^ 90 → 0 if val=90, 255 if val=165)
#   SET r5 = target_x
#   SET r6 = target_y
#   SET r9 = 1
#   SET r10 = r4 (= XOR result)
#   ADD r11 = r4 + r0 (= r4, since r0=0)
#   STORE at (r5, r6) regs 9,10,11,12
#     → writes (1, xor_result, xor_result, reg[12]) at (target_x, target_y)

# Let's just trace the decryption instructions directly
regs = [0] * 33
regs[1] = 90  # Set at (0,1)

# Walk instructions from (251,8) to (235,24)
x, y = 251, 8
while True:
    r, g, b, a = state[y][x]
    opcode = int(r)
    a1, a2, a3 = int(g), int(b), int(a)

    if opcode == 1:  # SET
        if 1 <= a1 <= 32:
            regs[a1] = a2 & 255
    elif opcode == 2:  # ADD
        if 1 <= a1 <= 32:
            regs[a1] = (regs[min(a2,32)] + regs[min(a3,32)]) & 255
    elif opcode == 4:  # XOR
        if 1 <= a1 <= 32:
            regs[a1] = regs[min(a2,32)] ^ regs[min(a3,32)]
    elif opcode == 8:  # STORE
        tx = regs[min(a1,32)]
        ty = regs[min(a2,32)]
        if not (tx == 0 and ty == 0):
            b0 = regs[min(a3, 32)]
            b1 = regs[min(a3+1, 32)]
            b2 = regs[min(a3+2, 32)]
            b3 = regs[min(a3+3, 32)]
            state[ty][tx] = [b0, b1, b2, b3]
    elif opcode == 5:  # JMP
        # This is the final JMP to (2,1) - drawing code
        print(f"JMP to ({a1},{a2}) at ({x},{y})")
        break

    x += 1
    if x > 255:
        x = 0
        y += 1
    if y > 127:
        break

print("Decryption done. Now tracing drawing code...")

# Phase 2: Now trace the drawing code from (2,1) to (250,8)
# Reset registers for drawing phase
regs = [0] * 33
regs[1] = 90  # Still set from before

# VRAM output: 128 rows x 256 cols
vram = np.zeros((128, 256), dtype=np.uint8)

x, y = 2, 1  # Start of drawing code after JMP
instr_count = 0
while True:
    r, g, b, a = state[y][x]
    opcode = int(r)
    a1, a2, a3 = int(g), int(b), int(a)

    if opcode == 0:
        pass
    elif opcode == 1:  # SET
        if 1 <= a1 <= 32:
            regs[a1] = a2 & 255
    elif opcode == 2:  # ADD
        if 1 <= a1 <= 32:
            regs[a1] = (regs[min(a2,32)] + regs[min(a3,32)]) & 255
    elif opcode == 3:  # SUB
        if 1 <= a1 <= 32:
            regs[a1] = (regs[min(a2,32)] - regs[min(a3,32)] + 256) & 255
    elif opcode == 4:  # XOR
        if 1 <= a1 <= 32:
            regs[a1] = regs[min(a2,32)] ^ regs[min(a3,32)]
    elif opcode == 7:  # VRAM write
        tx = regs[min(a1,32)]
        ty = regs[min(a2,32)]  # + 128 for actual VRAM position
        col = regs[min(a3,32)]
        if 0 <= ty <= 127:
            vram[ty][tx] = col
    elif opcode == 5:  # JMP
        if a1 == 250 and a2 == 8:
            print(f"Hit halt JMP at ({x},{y})")
            break
        # Other JMP - follow it
        x = a1
        y = max(1, min(a2, 127))
        continue
    elif opcode == 6:  # JNZ
        if regs[min(a1,32)] != 0:
            x = a2
            y = max(1, min(a3, 127))
            continue
    elif opcode == 9:  # LOAD
        if 1 <= a1 <= 32:
            sx = regs[min(a2,32)]
            sy = regs[min(a3,32)]
            regs[a1] = int(state[sy][sx][0])

    instr_count += 1
    x += 1
    if x > 255:
        x = 0
        y += 1
    if y > 127:
        x = 1
        y = 1

print(f"Drew {instr_count} instructions")

# Save VRAM as image
out = Image.fromarray(vram, mode='L')
out.save('output.png')
print("Saved output.png")

# Also save scaled up version
out_big = out.resize((512, 256), Image.NEAREST)
out_big.save('output_big.png')
print("Saved output_big.png")
