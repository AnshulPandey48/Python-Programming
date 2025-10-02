from functools import cmp_to_key
def compare(x,y):
    if str(x) + str(y) > str(y) + str(x):
        return -1
    else:
        return 1
    
def largest_number(nums):
    nums_sorted = sorted(nums,key=cmp_to_key(compare))
    largest_number = ''.join(map(str,nums_sorted))
    if largest_number[0] == "0":
        return "0"
    else:
        return largest_number

print(largest_number([3, 30, 34, 5, 9]))  # "9534330"
