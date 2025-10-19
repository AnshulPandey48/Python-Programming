s = "10212"
count = 0
freq = {} # dict is curly

for char in s:
    if len(freq) == 3:
        print(freq)
        exit()
        
    elif char in freq:
        freq[char]+=1
    else:
        freq[char] = 1

print(freq)
print(len(freq))