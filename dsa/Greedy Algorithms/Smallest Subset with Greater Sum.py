arr = [20,12,18,4]
count = 1
i = 0
j = 1
n = len(arr)
origi = arr[i]
while n > 0:
    maxi = sum(range(j,n))
    if origi < maxi:
        j+=1
        count+=1
        i+=1
        origi += arr[i]
    else:
        print(count)
        exit()
    n -=1
