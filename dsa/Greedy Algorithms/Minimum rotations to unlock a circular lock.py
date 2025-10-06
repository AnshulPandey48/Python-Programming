R = 222
D = 333
count = 0
while R > 0 and D > 0:
    digit1 = R % 10
    digit2 = D % 10
    diff1 = abs(digit1-digit2)
    diff2 = min(abs((9-digit1 + digit2),abs(9-digit2+digit1)))
    count += min(diff1,digit2)
print(count)