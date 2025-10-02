from collections import Counter
s = "cbacdcbc"
Counter = Counter(s)
seen = set()
stack = []

for ch in s:
    Counter[ch] -=1
    if ch in seen:
        continue
    while stack and ch < stack[-1] and Counter[stack[-1]] > 0:
        removed = stack.pop()
        seen.remove(removed)
    
    stack.append(ch)
    seen.add(ch)
print(stack)
result = "".join(map(str,stack))
print(result)