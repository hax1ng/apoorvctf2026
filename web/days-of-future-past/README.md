# Days of Future Past

**Category:** Web/Crypto | **Difficulty:** Hard (500 pts) | **Flag:** `apoorvctf{3v3ry_5y573m_h45_4_w34kn355}`

## Overview
A "CryptoVault" web application stores encrypted messages using XOR stream cipher with key reuse, requiring information disclosure exploitation followed by a many-time pad attack.

## Solution

### Step 1: Information Disclosure Chain
The HTML source contains developer comments revealing the API structure and a backup config path:
```html
<!-- Backup config was moved to /backup/ directory -->
<!-- See /static/js/app.js for frontend API integration -->
```

`app.js` reveals the debug endpoint requires an `X-API-Key` header and references `/backup/config.json.bak`.

Fetching the backup config gives us the API key:
```json
{"api_key": "d3v3l0p3r_acc355_k3y_2024", "jwt_algorithm": "HS256"}
```

### Step 2: JWT Secret Recovery
The `/api/v1/debug` endpoint (authenticated with the API key) leaks the JWT secret derivation hint:
> "Company name (lowercase) concatenated with founding year"

Plus the SHA256 hash for verification. The secret is `cryptovault2026`.

### Step 3: Admin JWT Forgery
Forge a JWT with `role: admin` using the recovered secret to access `/api/v1/vault/messages`, which returns 15 XOR-encrypted messages.

### Step 4: Many-Time Pad Attack
All messages are encrypted with the same XOR keystream. Using statistical analysis (frequency of spaces and letters across ciphertext pairs), we partially recover the keystream. Message 13 partially decrypts to reveal it contains the flag in leetspeak format.

Using the guessed plaintext `"the real flag is apoorvctf{3v3ry_5y573m_h45_4_w34kn355} and all others are distractions"` as a crib, we derive the full keystream and confirm all 15 messages decrypt to coherent English.

## Key Takeaways
- Always check HTML comments, JS source, and robots.txt for information leaks
- Backup files left on web servers are a classic vulnerability
- XOR encryption with key reuse (many-time pad) is trivially breakable via crib dragging
- Statistical analysis of ciphertext pairs exploits the structure of natural language
