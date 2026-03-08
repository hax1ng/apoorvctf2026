# Hefty Secrets

**Category:** AI | **Difficulty:** Medium | **Flag:** `apoorvctf{l0r4_m3rg3}`

## Overview
Two PyTorch checkpoints — a base model and a LoRA adapter — that when merged reveal a hidden flag encoded as a bitmap in the weight matrix.

## Solution

The challenge provides two directories in PyTorch's unzipped checkpoint format:
- `base_model/` — a simple neural network with layers including a 256×256 weight matrix at layer2
- `lora_adapter/` — a rank-64 LoRA decomposition (lora_A: 64×256, lora_B: 256×64) targeting layer2

LoRA (Low-Rank Adaptation) merging works by adding the product of the two low-rank matrices to the original weight: `W' = W + B @ A`.

After merging, the resulting 256×256 matrix contains values extremely close to either 0 or 1 (within floating-point epsilon). Thresholding at 0.5 and rendering as a 1-bit bitmap image reveals the flag text.

```python
import torch
from PIL import Image
import numpy as np

base = torch.load('base_model.pt', map_location='cpu', weights_only=False)
lora = torch.load('lora_adapter.pt', map_location='cpu', weights_only=False)

merged = base['layer2.weight'] + lora['layer2.lora_B'] @ lora['layer2.lora_A']
binary = (merged > 0.5).int().numpy().astype(np.uint8)
img = Image.fromarray((1 - binary) * 255)
img.save('flag.png')
```

## Key Takeaways
- LoRA adapters modify base model weights via low-rank matrix addition: `W' = W + BA`
- Weight matrices can encode arbitrary data — here a 256×256 binary image
- PyTorch's unzipped checkpoint format stores `data.pkl` + numbered data files in a directory structure; re-zipping them allows normal `torch.load()`
