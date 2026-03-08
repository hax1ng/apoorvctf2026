#!/usr/bin/env python3
"""Resonance Lock: UART baud-rate calibration + 512-bit multiplier CTF solver."""

import socket
import time

HOST = "chals4.apoorvctf.xyz"
PORT = 1337

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.settimeout(5)
sock.connect((HOST, PORT))

# Step 1: Send 0xCA to enter calibration mode
sock.send(bytes([0xCA]))
time.sleep(0.3)
try:
    sock.recv(4096)
except socket.timeout:
    pass

# Step 2: Send 5 calibration bursts of 64x 0x55
for i in range(10):
    sock.send(bytes([0x55] * 64))
    time.sleep(0.5)
    try:
        resp = sock.recv(4096)
        print(f"Burst {i+1}: {resp.decode().strip()}")
        if b"LOCKED" in resp:
            break
    except socket.timeout:
        pass

# Step 3: Send 0xAA + 64-byte A + 64-byte B (512-bit operands)
A = b'\x00' * 63 + b'\x02'  # A = 2
B = b'\x00' * 63 + b'\x03'  # B = 3
sock.send(bytes([0xAA]) + A + B)
time.sleep(2)

resp = sock.recv(4096).decode().strip()
print(resp)
sock.close()
