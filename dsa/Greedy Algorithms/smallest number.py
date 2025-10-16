s = 9
d = 2
value = 1
sd = [value]*d
print(sd)
sum1 = 0
i = d
while i > 0:
    sum1 = sum(sd)
    if sum1 < s:
        newv = s - sum1
        if newv > 9:
            sd[i] = 9
            sd[i-1] = sum1 - 9
        else:
            sd[i] = s - sum1
    if sum1 == s:
        print(sd)
        exit()
print(-1)
    
