s = 9
d = 2
#handling edge cases 
if (s == 0 and d < 1) or (s > 9*d):
    print(-1)
    exit()
else:
    sd = [0]*d
    sd[0] = 1
    i = d-1
    s -=1
    while i >=0 and s > 0:
        add = min(9-sd[i],s)
        i-=1
        sd[i] += add
        s -= add
    res = ''.join(map(str,sd))
print(res)