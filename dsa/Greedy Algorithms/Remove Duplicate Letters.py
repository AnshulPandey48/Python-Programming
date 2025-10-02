s = "cbacdcbc"
r = ""
d1 = {}
prev = ""
for ch in s:
    if ch in d1 and ch < prev:
        del d1[ch]
    d1[ch] = True
    prev = ch
print(d1)

r = list(d1.keys())
result = ''.join(map(str,r))
print(result)
