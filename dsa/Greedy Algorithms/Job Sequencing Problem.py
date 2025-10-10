deadline = [3,1,2,2]
profit = [50,15,20,30]
deadline_profit = [(i,d,p) for i , (d,p) in enumerate(zip(deadline,profit))]
deadline_profit.sort(reverse= True,key = lambda x : x[2])
count = 0
res = []
i = 0
sum1 = 0
while i < len(deadline_profit):
    if count < deadline_profit[i][1]:
        count +=1
        sum1 += deadline_profit[i][2]
    i+=1
res.append(count)
res.append(sum1)
print(res)

