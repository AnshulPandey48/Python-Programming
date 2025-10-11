deadline = [4, 1, 1, 1]
profit = [20,10,30,40]
jobs = [(d,p) for d,p in zip(deadline,profit)]
jobs.sort(reverse= True , key = lambda x : x[1])
max_deadline = max(deadline)
parent = [i for i in range(max_deadline+1)]
def find(slot):
    if parent[slot] != slot:
        parent[slot] = find(parent[slot])
    return parent[slot]

for d , p in jobs:
    avail = find(d)
    if avail > 0:
        total_profit += p
        count +=1
        parent[avail]= avail -1
print ([count,total_profit])