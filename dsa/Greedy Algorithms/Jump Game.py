arr = [1,0,2]
curr_pos = 0
poss_steps = arr[0]

while curr_pos <= len(arr)-1:
    if arr[curr_pos] == 0:
        print(False)
        exit()
    curr_pos += arr[curr_pos]

print(True)