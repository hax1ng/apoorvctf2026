# KameHame-Hack

**Category:** Web | **Difficulty:** Hard (500) | **Flag:** `apoorvctf{J1nj4_N1nj4_baybay}`

## Overview
A Dragon Ball Z-themed Flask web app where you fight through 3 stages. The final boss (Jiren) has 1,000,000 power — far beyond your 70,000. You need to "rewrite your stats" using Jinja2 SSTI.

## Solution

The app is a Flask + Jinja2 game where your fighter name is stored in a session cookie and rendered through `render_template_string()` during the `/attack` endpoint. This creates a **Server-Side Template Injection (SSTI)** vulnerability.

The key constraint: **quotes are filtered**. Any single or double quotes in the name break the template rendering and return `ERROR`. This blocks most standard SSTI payloads that need string literals.

The JS source contains a hint: *"To surpass a God, one must update() their inner `__dict__`ionary."* This points to Python's `__dict__` attribute manipulation.

The `player` object is available in the Jinja2 template context. Using **keyword arguments** (which don't need quotes), we can call:

```
{{player.__dict__.update(power_level=9999999) or player.name}}
```

- `player.__dict__.update(power_level=9999999)` — sets power to 9,999,999
- `or player.name` — ensures the rendered output is non-empty (empty string triggers ERROR)

The SSTI executes during each attack, boosting power before the fight comparison. With 9,999,999 power, all 3 stages (including Jiren at 1,000,000) are defeated.

See `solve.py` for the full exploit.

## Key Takeaways
- Jinja2 SSTI doesn't always mean RCE — sometimes you just need to modify in-scope objects
- When quotes are filtered, Python keyword arguments (`key=value`) bypass the restriction
- `__dict__.update()` with kwargs is a powerful SSTI primitive for modifying object attributes
- Always check JS comments and HTML comments for hints about the vulnerability
