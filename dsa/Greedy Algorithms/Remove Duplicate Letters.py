from collections import Counter
s = "cbacdcbc"
Counter = Counter(s)
seen = set()
stack = []

for ch in s:
    Counter[ch] -=1
    if ch in seen:
        continue
    