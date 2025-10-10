class Solution:
    def jobSequencing(self, deadline, profit):
        jobs = [(d, p) for d, p in zip(deadline, profit)]
        jobs.sort(key=lambda x: x[1], reverse=True)  # sort by profit descending

        max_deadline = max(deadline)
        parent = [i for i in range(max_deadline + 1)]  # Union-Find array

        def find(slot):
            if parent[slot] != slot:
                parent[slot] = find(parent[slot])
            return parent[slot]

        count = 0
        total_profit = 0

        for d, p in jobs:
            available = find(d)  # find latest free slot
            if available > 0:
                total_profit += p
                count += 1
                parent[available] = available - 1  # mark slot as filled

        return [count, total_profit]
