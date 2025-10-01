import numpy as np
arr = np.random.randint(0,10,10)
print(arr)
#maximum element of an array
print(max(arr))
print(min(arr))
for i in range(len(arr)):
    if(arr[i] % 2 == 0):
        print(f"indices are : {i}\n")
print("\n")
#to find the mean of an array
data = [1,3,5,5,0,2,4]
mean_val = np.mean(data)
print("mean value : {mean_val}")