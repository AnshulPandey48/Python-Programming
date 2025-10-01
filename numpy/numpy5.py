import numpy as np
arr = np.random.randint(1,20,10)
print(arr)
for i in range (len(arr)):
    if(arr[i] % 2 == 0):
        #print(arr[i])
        print(i)