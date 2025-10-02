s = "bcabc"
#op -> "abc"
r = ""
d1 = {}
for ch in s:
    if ch in d1:
        del d1[ch]
    d1[ch] = True
print(d1)

r = d1.keys()