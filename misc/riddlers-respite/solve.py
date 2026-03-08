#!/usr/bin/env python3
"""Solve script for Riddler's Respite (misc, 500pts)"""
import socket, time, re

s = socket.socket()
s.settimeout(15)
s.connect(('chals1.apoorvctf.xyz', 13001))

# Function: f(array) = XOR(all elements) * (length of consecutive prefix from 0)
# prefix = longest run {0, 1, 2, ..., k} present in the array
#
# Required outputs: [0, 20, 69, 12345, 720764]
#
# For output 0: array without 0 -> f = 0
# For output T (small): [0, T] -> XOR=T, prefix_len=1, f=T
# For output 720764 (too large for single element, max=100000):
#   720764 = 11 * 65524
#   Use prefix {0..10} (prefix_len=11), add element 65535 to get XOR=65524

arrays = [
    [1, 2, 3, 4, 5],                                      # -> 0
    [0, 20],                                                # -> 20
    [0, 69],                                                # -> 69
    [0, 12345],                                             # -> 12345
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 65535],            # -> 720764
]

payload = 'password\n1\n5\n'
for arr in arrays:
    payload += f"{len(arr)} {' '.join(map(str, arr))}\n"

s.send(payload.encode())
time.sleep(5)

data = b''
try:
    while True:
        chunk = s.recv(4096)
        if not chunk: break
        data += chunk
except: pass
s.close()

text = re.sub(rb'\x1b\[[0-9;]*m', b'', data).decode(errors='replace')
print(text)
