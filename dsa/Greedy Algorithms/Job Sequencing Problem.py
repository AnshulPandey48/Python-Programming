deadline = [4, 1, 1, 1]
profit = [20, 10, 40,30]
res = []
count = 0
total_profit = 0
deadline_profit = [(i,d,p) for i ,(d,p) in enumerate(zip(deadline,profit))]

deadline_profit.sort(reverse= True,key= lambda x: x[2])

for i in range(len(deadline_profit)):
    if deadline_profit[i][1] >=  count:
        total_profit += deadline_profit[i][2]
        count+=1

res.append(count,total_profit)
print(res)