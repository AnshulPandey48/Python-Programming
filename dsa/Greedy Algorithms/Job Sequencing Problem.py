deadline = [3,1,2,2]
profit = [50,15,20,30]
deadline_profit = [(i,d,p) for i , (d,p) in enumerate(zip(deadline,profit))]
deadline_profit.sort(reverse= True,key = lambda x : x[2])
count = 0
max_index = max(deadline)
slots = [None]*(max_index+1) # index 0 ... max_index
index_place = 0
while count != len(deadline_profit):
    if 