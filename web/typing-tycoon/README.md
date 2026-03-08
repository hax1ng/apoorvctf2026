# Typing Tycoon

**Category:** Web | **Difficulty:** Medium | **Flag:** `apoorvctf{typ1ng_f4st3r_th4n_sh3ll_1nj3ct10n}`

## Overview
A TypeRacer clone where you race against three AI bots (Marc, Pecco, Fabio) that always run at 1.25x your progress, making them impossible to beat normally.

## Solution

### 1. Reconnaissance
The app is a Next.js frontend proxying to a Go backend with three API endpoints:
- `POST /api/v1/race/start` — starts a race, returns JWT token, text, and race_id
- `POST /api/v1/race/sync` — sends typed words, returns bot/user progress
- `GET /api/v1/stats?id=N` — user stats (has a SQLi red herring)

### 2. JWT Analysis
The race start endpoint returns a JWT with `alg: HS256`:
```json
{"role": "user", "speed_boost": false, "sub": "racer_XXXXX"}
```

The `speed_boost: false` claim is interesting — setting it to `true` should slow down the bots.

### 3. JWT alg:none Attack
The server accepts JWTs with `alg: none` (no signature verification). By forging a token with `speed_boost: true`, the bots are reduced from ~120+ WPM to ~0.9 WPM:

```python
header = {"alg": "none", "typ": "JWT"}
payload = {"exp": 9999999999, "role": "admin", "speed_boost": True, "sub": "racer_12345"}
# base64url encode header and payload, append empty signature
forged_token = f"{b64(header)}.{b64(payload)}."
```

### 4. Automated Race
With the forged JWT slowing bots to a crawl, a script sends all 120 words to the sync endpoint. The bots barely move while we complete the race, triggering the victory condition and revealing the flag.

### Red Herring
The `/api/v1/stats?id=` endpoint shows SQLite error messages with the full query, suggesting SQL injection. An HTML comment hints at `/tmp/bot_multiplier.conf`. However, the errors are either fabricated or the query is parameterized — no actual injection is possible. The real vulnerability is the JWT `alg:none` bypass.

## Key Takeaways
- Always check for JWT `alg:none` vulnerabilities — many servers fail to enforce algorithm verification
- Don't get baited by obvious-looking SQLi that shows error messages — it can be a honeypot
- Read JWT claims carefully — `speed_boost: false` is a hint about what to change
- When racing against bots, think about slowing them down rather than speeding yourself up
