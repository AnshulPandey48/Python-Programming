deadline = [3,1,2,2]
profit = [50,15,20,30]
deadline_profit = [(i,d,p) for i , (d,p) in enumerate(zip(deadline,profit))]
deadline_profit.sort(reverse= True,key = lambda x : x[2])
count = 0
sum1 = 0
max_index = max(deadline)
slots = [None]*(max_index+1) # index 0 ... max_index
index_place = 0
i = 0
while i != len(deadline_profit):
    if count == max_index:
        break
    index_place = deadline_profit[i][1]
    if slots[index_place] is None:
        slots[index_place] = deadline_profit[i][2]
        count +=1
        sum1 += deadline_profit[i][2]
    else:
        index_place -=1
        slots[index_place] = deadline_profit[i][2]
        sum1 += deadline_profit[i][2]
        count +=1
    i+=1
print(count)
print(sum1)

