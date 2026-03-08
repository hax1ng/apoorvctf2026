# Routine Checks

**Category:** Forensics | **Difficulty:** 500 | **Flag:** `apoorvctf{b1ts_wh1sp3r_1n_th3_l0w3st_b1t}`

## Overview
A PCAP file containing routine text messages between network nodes, with one connection sending a JPEG image instead of text.

## Solution

1. **PCAP analysis**: The capture contains ~70 TCP conversations on ports 5000-5069, all on localhost. Most carry routine text messages like "System health check OK." and "Network latency seems stable."

2. **Identify the outlier**: Port 5001 stands out — instead of text, it carries a much larger payload (~5.7KB of binary data). The TCP conversation stats show it has 6,026 bytes vs ~650-1200 for all others.

3. **Extract the image**: The payload is a JPEG with a corrupted first byte (`0x3f` instead of `0xff`). Fixing the first byte gives a valid JPEG containing a QR code.

   ```bash
   tshark -r challenge.pcap -Y "tcp.port==5001 && data" -T fields -e data | xxd -r -p > raw_data.bin
   python3 -c "d=bytearray(open('raw_data.bin','rb').read()); d[0]=0xff; open('extracted.jpg','wb').write(d)"
   ```

4. **QR code decoy**: The QR code decodes to `apoorvctf{this_aint_it_brother}` — a fake flag.

5. **Steganography**: Running `steghide info extracted.jpg` with an empty passphrase reveals an embedded file `realflag.txt` (42 bytes, AES-128-CBC encrypted).

   ```bash
   steghide extract -sf extracted.jpg -p ""
   cat realflag.txt
   ```

6. The extracted file contains the real flag.

## Key Takeaways
- Decoy flags are common in CTFs — always verify and look deeper.
- When you find a JPEG in a forensics challenge, always check for steghide-embedded data.
- An empty passphrase is worth trying first with steghide.
- The corrupted first byte was a hint that the image was tampered with / hidden.
