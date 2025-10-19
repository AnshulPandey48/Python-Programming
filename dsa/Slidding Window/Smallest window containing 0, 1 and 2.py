def smallestsubstring(s):
    left = 0
    count = {'0':0,'1':0,'2':0}
    min_len = float('inf')
    for right in range(len(s)):
        count(s[right])+=1
    while count['0'] > 0 and count['1'] > 0 and count['2'] > 0:
        min_len = min(min_len,right - left+1)
        count(s[left])-=1
        left +=1

    if min_len != float('inf'):
        print(min_len)
    else:
        print(-1)

