arr = [100, 200, 300, 400]
k = 2
sum1 = 0
for i in range(k):
    sum1 += arr[i]
current = 0
curr_max = sum1
while k<= len(arr)-1:
    sum1 -= arr[current]
    sum1 += arr[k]
    curr_max = max(curr_max,sum1)
    k+=1
    current+=1


print(curr_max)
