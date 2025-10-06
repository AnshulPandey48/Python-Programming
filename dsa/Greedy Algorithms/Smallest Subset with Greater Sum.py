arr = [66,53,87,23 ,58 ,19]
arr.sort(reverse=True)
print()
count = 1
i = 0
j = 1
n = len(arr)
origi = arr[i]
while n > 0:
    maxi = sum((arr[j:n])) # j is starting n is len(arr) -1
    if origi < maxi:
        j+=1
        count+=1
        i+=1
        origi += arr[i]
    else:
        print(count)
        exit()
    n -=1
