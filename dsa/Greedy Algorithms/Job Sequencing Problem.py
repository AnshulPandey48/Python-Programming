deadline = [4, 1, 1, 1]
profit = [20, 10, 40,30]

deadline_profit = [(i,d,p) for i ,(d,p) in enumerate(zip(deadline,profit))]
print(deadline_profit)

deadline_profit.sort(key= lambda x: x[2])
print(deadline_profit)