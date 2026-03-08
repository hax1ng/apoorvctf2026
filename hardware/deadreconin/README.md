# deaDr3con'in

**Category:** Hardware | **Difficulty:** Hard (500 pts) | **Flag:** `apoorvctf{f'GS}`

## Overview
A damaged CNC controller firmware binary contains an XOR-encrypted G-code job that was engraving text when power was cut. Recover the engraved text to find the flag.

## Solution

1. **Firmware structure**: The 20KB binary is an ARM Cortex-M firmware with a clear layout: vector table, NOP padding, strings section, config struct, and a job buffer starting at offset 0x1000 with header "JBUFHDR5SEG4".

2. **Identify encryption**: The job buffer payload at 0x1010 is XOR-encrypted. The firmware strings mention "JOB BUFFER FRAGMENTED" and "packet format [4B:length][1B:seg_id][NB:data] x4 segments", telling us the data is split into 4 segments.

3. **Derive XOR key**: Brute-forced each byte of an 8-byte repeating XOR key by scoring decrypted output against valid G-code characters (`G0123456789. -XYZIJF\n`). The winning key: `08 f1 4c 3b a7 2e 91 c4`.

4. **Decrypt all segments**: The main payload (seg 4/4) decrypts with key offset 0. Three additional segment packets follow after offset 0x1FA2, each with a [4B:length][1B:seg_id] header. These decrypt with key offset 1. Segments are stored out of order (4, 1, 3, 2).

5. **Parse and plot G-code**: The decrypted G-code contains G00/G01/G02/G03 commands defining cutting paths. Parsing the arcs (with I,J center offsets) and plotting the toolpath reveals four characters rotated ~39 degrees: **f ' G S**.

6. **Read the flag**: The engraved text is `f'GS`. Per the challenge instructions, wrapping gives `apoorvctf{f'GS}`.

## Key Takeaways
- CNC G-code is highly structured - valid character frequency analysis per byte position is an effective crib for XOR key recovery.
- Fragmented/out-of-order segments require careful reassembly using seg_id fields.
- Key offset can differ between segments even with the same key bytes.
- G02/G03 arc interpolation with I,J center offsets is essential for correct CNC toolpath rendering.
