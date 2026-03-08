# Riddler's Respite

**Category:** Misc | **Difficulty:** Hard (500pts) | **Flag:** `apoorvctf{m3xtim3sx0r}`

## Overview
A netcat service presents a riddle: given a black-box function over arrays, provide 5 arrays that produce specific target outputs [0, 20, 69, 12345, 720764].

## Solution

### Reverse-engineering the function

Connected to the service (`nc chals1.apoorvctf.xyz 13001`), which asks for a password (any input works), then presents a riddle asking for arrays of numbers.

The input format is: `cnt` (number of test cases), then for each test case, `N a1 a2 ... aN` on one line.

Through systematic testing, discovered the function:

**f(array) = XOR(all elements) × prefix_length**

Where `prefix_length` is the length of the longest consecutive integer sequence starting from 0 present in the array (e.g., if the array contains {0, 1, 2, 5}, the prefix is {0, 1, 2} with length 3).

Key observations used to deduce this:
1. Arrays without a 0 element always return 0
2. The function is order-independent (symmetric over permutations)
3. Adding extra zeros doesn't change the result
4. For arrays {0, k} where k ≥ 2, the output equals k (XOR=k, prefix_len=1)
5. For identity arrays {0,1,...,N-1}, output = XOR(0..N-1) × N

### Constructing solution arrays

- **Target 0**: `[1, 2, 3, 4, 5]` — no zero element, so output is 0
- **Target 20**: `[0, 20]` — XOR=20, prefix_len=1, 20×1=20
- **Target 69**: `[0, 69]` — XOR=69, prefix_len=1, 69×1=69
- **Target 12345**: `[0, 12345]` — XOR=12345, prefix_len=1, 12345×1=12345
- **Target 720764**: Can't use `[0, 720764]` because max element value is 100000. Instead: 720764 = 11 × 65524. Use prefix {0..10} (length 11) plus element 65535 to achieve XOR=65524. Array: `[0,1,2,3,4,5,6,7,8,9,10,65535]`

The flag name `m3xtim3sx0r` confirms the function: "M times XOR" (prefix_length × XOR).

## Key Takeaways
- Black-box function analysis: test systematically with controlled inputs (zeros, identity sequences, permutations)
- XOR properties are common in CTF math/misc challenges
- When values are capped, decompose the target using factorization and adjust the prefix length accordingly
