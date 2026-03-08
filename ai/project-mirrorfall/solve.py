#!/usr/bin/env python3
"""Project Mirrorfall solver"""

from sentence_transformers import SentenceTransformer

# Objective 1: Variable X
# Latest commit SHA for documents/2013/20130905-theguardian__bullrun.pdf
# in iamcryptoki/snowden-archive repo
commit_sha = "7d88323521194ed8598624dc3a932930debdde1d"
X = commit_sha[:7]  # 7d88323

# Objective 2: ECI codeword
# From PDF Appendix A remarks: APERIODIC, AMBULANT, AUNTIE, ...
# Second ECI (8 letters) = AMBULANT
eci_codeword = "ambulant"  # normalized to lowercase

# Objective 3: Variable Y
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(eci_codeword)
Y = round(float(embedding[0]), 4)

flag = f"apoorvctf{{{X}_{Y}}}"
print(f"Variable X: {X}")
print(f"ECI codeword: {eci_codeword}")
print(f"Variable Y: {Y}")
print(f"Flag: {flag}")
