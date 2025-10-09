prices = [3, 2, 1, 4,5]
k = 4
prices.sort()
# 1 , 2 , 3 , 4
res = []
i,j = 0 , len(prices)
sum1 = 0
while i < j:
    sum1 += prices[i]
    j -= k
    i+=1
res.append(sum1)
i, j = 0 , len(prices) -1
sum2 = 0
while i <= j:
    sum2 += prices[j]
    j-=1
    i += k

res.append(sum2)

print(res)
