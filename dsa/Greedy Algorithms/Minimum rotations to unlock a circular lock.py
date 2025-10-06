R = 2345 
D = 5432
count = 0
while R > 0 and D > 0:
    digit1 = R % 10
    digit2 = D % 10
    diff1 = abs(digit1-digit2)
    diff2 = 10 - digit2
    count += min(diff1,digit2)
    R //= 10
    D //= 10
print(count)