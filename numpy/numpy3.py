import numpy as np
arr = np.array([5,10,15,20,25,30])
for i in range(len(arr)):
    if arr[i] > 20:
        arr[i] = -1
print(arr)