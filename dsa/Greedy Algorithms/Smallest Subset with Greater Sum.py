arr = [66,53,87,23 ,58 ,19]
arr.sort(reverse=True)
print(arr)
count = 1
i = 0
n = len(arr)
origi = arr[i]
while n > 0:
    maxi = sum(arr[i+1:]) 
    if origi <= maxi:
        count+=1
        i+=1
        origi += arr[i]
    else:
        print (count)
    n -=1
