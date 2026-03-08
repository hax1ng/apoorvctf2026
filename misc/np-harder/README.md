# NP Harder

**Category:** Misc | **Difficulty:** Easy | **Flag:** `apoorvctf{N4v4r_givinggg_u_up}`

## Overview
A netcat service presents a large random graph and asks you to "submit your answer" — but it's a rickroll that accepts any input.

## Solution
1. Connect to `chals2.apoorvctf.xyz:14001`
2. The server displays a graph with 200 nodes and ~230 edges, framed as an NP-hard problem
3. Submit literally anything — the server responds with the flag
4. The YouTube link in the output is a rickroll, and the flag is a leetspeak "Never giving you up"

The entire NP-hard framing is a red herring. The challenge is a troll/rickroll.

## Key Takeaways
- Always try the simplest thing first — submitting arbitrary input before attempting to solve the stated problem.
- CTF misc challenges love trolls. If something seems impossibly hard, it might just be a joke.
