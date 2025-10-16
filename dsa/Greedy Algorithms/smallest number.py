s = 9
d = 2
if (s == 0 and d > 1) or s > 9 * d:
    print(-1)
    exit()
else:
    sd = [0]*d
    s-=1
    sd[0] = 1
    print(sd)

    i = d -1
    while i >= 0 and s> 0:
        add = min(9 - sd[i],s)
        sd[i] += add
        s-= add
        i -=1 
print("Smallest number: ",''.join (map(str,sd)))