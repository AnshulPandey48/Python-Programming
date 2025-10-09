arr = [1,2,0,3,0,0]
curr_pos = 0
poss_steps = arr[0]

while curr_pos <= len(arr):
    if arr[curr_pos] == 0:
        print(False)
        exit()
        