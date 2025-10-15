arr = [900, 940, 950, 1100, 1500, 1800]
dep = [910, 1200, 1120, 1130, 1900, 2000]
arr.sort()
dep.sort()
i = 1
j = 0
platform = 1
max_platform = 1
n = len(arr)
while i < n and j < n:
    if dep[j] >= arr[i]:
        platform+=1
        i+=1
    else:
        j +=1
        platform -=1
    max_platform = max(platform,max_platform)

print(max_platform)